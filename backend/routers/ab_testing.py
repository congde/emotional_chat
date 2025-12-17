#!/usr/bin/env python3
"""
A/B测试相关路由
提供实验管理、分组分配、数据分析等API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from backend.ab_testing import ABTestManager, ABTestConfig, get_ab_test_manager
from backend.ab_testing.analyzer import ABTestAnalyzer
from backend.database import DatabaseManager, ABTestExperiment, ABTestEvent, ABTestGroupAssignment
from backend.logging_config import get_logger
import json

router = APIRouter(prefix="/ab-testing", tags=["A/B测试"])
logger = get_logger(__name__)

# 初始化A/B测试管理器
ab_test_manager = get_ab_test_manager()


# ============ 请求/响应模型 ============

class ExperimentCreateRequest(BaseModel):
    """创建实验请求"""
    experiment_id: str
    name: str
    description: str
    groups: List[str] = ["A", "B"]
    weights: List[float] = [0.5, 0.5]
    start_date: str  # ISO格式日期字符串
    end_date: Optional[str] = None
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None


class ExperimentResponse(BaseModel):
    """实验响应"""
    experiment_id: str
    name: str
    description: str
    groups: List[str]
    weights: List[float]
    start_date: str
    end_date: Optional[str]
    enabled: bool
    metadata: Dict[str, Any]
    is_active: bool


class GroupAssignmentRequest(BaseModel):
    """分组分配请求"""
    user_id: str
    experiment_id: str
    force_group: Optional[str] = None  # 强制分配到指定组（用于测试）


class GroupAssignmentResponse(BaseModel):
    """分组分配响应"""
    user_id: str
    experiment_id: str
    group: str
    assigned_at: str


class AnalysisRequest(BaseModel):
    """分析请求"""
    experiment_id: str
    metrics: Optional[List[str]] = None  # 要分析的指标列表
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class AnalysisResponse(BaseModel):
    """分析响应"""
    experiment_id: str
    metrics: Dict[str, Any]
    statistical_tests: Dict[str, Any]
    report: str


# ============ API端点 ============

@router.post("/experiments", response_model=ExperimentResponse)
async def create_experiment(request: ExperimentCreateRequest):
    """
    创建新的A/B测试实验
    """
    try:
        # 解析日期
        start_date = datetime.fromisoformat(request.start_date.replace("Z", "+00:00"))
        end_date = None
        if request.end_date:
            end_date = datetime.fromisoformat(request.end_date.replace("Z", "+00:00"))
        
        # 创建实验配置
        config = ABTestConfig(
            experiment_id=request.experiment_id,
            name=request.name,
            description=request.description,
            groups=request.groups,
            weights=request.weights,
            start_date=start_date,
            end_date=end_date,
            enabled=request.enabled,
            metadata=request.metadata or {}
        )
        
        # 注册实验
        ab_test_manager.register_experiment(config)
        
        # 保存到数据库
        with DatabaseManager() as db:
            experiment = ABTestExperiment(
                experiment_id=request.experiment_id,
                name=request.name,
                description=request.description,
                groups=json.dumps(request.groups),
                weights=json.dumps(request.weights),
                start_date=start_date,
                end_date=end_date,
                enabled=request.enabled,
                metadata=json.dumps(request.metadata or {})
            )
            db.add(experiment)
            db.commit()
        
        return config.to_dict()
    
    except Exception as e:
        logger.error(f"创建实验失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments", response_model=List[ExperimentResponse])
async def list_experiments(enabled: Optional[bool] = None):
    """
    列出所有实验
    """
    try:
        experiments = ab_test_manager.list_experiments()
        
        if enabled is not None:
            experiments = [e for e in experiments if e.get("enabled") == enabled]
        
        return experiments
    except Exception as e:
        logger.error(f"列出实验失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str):
    """
    获取实验详情
    """
    try:
        config = ab_test_manager.get_experiment(experiment_id)
        if not config:
            raise HTTPException(status_code=404, detail="实验不存在")
        return config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取实验失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assign", response_model=GroupAssignmentResponse)
async def assign_group(request: GroupAssignmentRequest):
    """
    为用户分配实验组
    """
    try:
        group = ab_test_manager.assign_user_to_group(
            user_id=request.user_id,
            experiment_id=request.experiment_id,
            force_group=request.force_group
        )
        
        if not group:
            raise HTTPException(
                status_code=400,
                detail="无法分配组：实验不存在或未激活"
            )
        
        # 保存分配记录到数据库
        with DatabaseManager() as db:
            # 检查是否已存在分配
            existing = db.query(ABTestGroupAssignment).filter(
                ABTestGroupAssignment.user_id == request.user_id,
                ABTestGroupAssignment.experiment_id == request.experiment_id
            ).first()
            
            if existing:
                existing.group = group
                existing.updated_at = datetime.utcnow()
            else:
                assignment = ABTestGroupAssignment(
                    user_id=request.user_id,
                    experiment_id=request.experiment_id,
                    group=group
                )
                db.add(assignment)
            
            db.commit()
        
        return {
            "user_id": request.user_id,
            "experiment_id": request.experiment_id,
            "group": group,
            "assigned_at": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分配组失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assign/{experiment_id}/{user_id}")
async def get_user_group(experiment_id: str, user_id: str):
    """
    获取用户已分配的组
    """
    try:
        group = ab_test_manager.group_assigner.get_user_group(
            user_id=user_id,
            experiment_id=experiment_id
        )
        
        if not group:
            # 尝试从数据库查询
            with DatabaseManager() as db:
                assignment = db.query(ABTestGroupAssignment).filter(
                    ABTestGroupAssignment.user_id == user_id,
                    ABTestGroupAssignment.experiment_id == experiment_id
                ).first()
                
                if assignment:
                    group = assignment.group
        
        if not group:
            return {"user_id": user_id, "experiment_id": experiment_id, "group": None}
        
        return {
            "user_id": user_id,
            "experiment_id": experiment_id,
            "group": group
        }
    
    except Exception as e:
        logger.error(f"获取用户组失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_experiment(request: AnalysisRequest):
    """
    分析实验数据
    """
    try:
        # 初始化分析器
        analyzer = ABTestAnalyzer()
        
        # 从数据库加载事件数据
        with DatabaseManager() as db:
            query = db.query(ABTestEvent).filter(
                ABTestEvent.experiment_id == request.experiment_id
            )
            
            if request.start_date:
                start_dt = datetime.fromisoformat(request.start_date.replace("Z", "+00:00"))
                query = query.filter(ABTestEvent.timestamp >= start_dt)
            
            if request.end_date:
                end_dt = datetime.fromisoformat(request.end_date.replace("Z", "+00:00"))
                query = query.filter(ABTestEvent.timestamp <= end_dt)
            
            events = query.all()
        
        # 转换为DataFrame格式
        import pandas as pd
        events_data = []
        for event in events:
            events_data.append({
                "user_id": event.user_id,
                "experiment_id": event.experiment_id,
                "group": event.group,
                "event": event.event_type,
                "timestamp": event.timestamp.timestamp(),
                "data": json.loads(event.event_data) if isinstance(event.event_data, str) else event.event_data
            })
        
        if not events_data:
            raise HTTPException(status_code=404, detail="实验数据不足")
        
        analyzer.df = pd.DataFrame(events_data)
        
        # 计算指标
        metrics = analyzer.calculate_metrics(
            experiment_id=request.experiment_id,
            metrics=request.metrics
        )
        
        # 进行统计检验
        statistical_tests = {}
        if len(metrics) >= 2:
            groups = sorted(metrics.keys())
            group_a, group_b = groups[0], groups[1]
            
            for metric_name in ["user_rating", "response_time"]:
                if any(metric_name in m for m in metrics.values()):
                    test_result = analyzer.statistical_test(
                        experiment_id=request.experiment_id,
                        metric=metric_name,
                        group_a=group_a,
                        group_b=group_b
                    )
                    if "error" not in test_result:
                        statistical_tests[metric_name] = test_result
        
        # 生成报告
        report = analyzer.generate_report(request.experiment_id)
        
        return {
            "experiment_id": request.experiment_id,
            "metrics": metrics,
            "statistical_tests": statistical_tests,
            "report": report
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析实验失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments/{experiment_id}/stats")
async def get_experiment_stats(experiment_id: str):
    """
    获取实验统计信息
    """
    try:
        with DatabaseManager() as db:
            # 总事件数
            total_events = db.query(ABTestEvent).filter(
                ABTestEvent.experiment_id == experiment_id
            ).count()
            
            # 各组事件数
            group_counts = {}
            groups = db.query(ABTestEvent.group).filter(
                ABTestEvent.experiment_id == experiment_id
            ).distinct().all()
            
            for (group,) in groups:
                count = db.query(ABTestEvent).filter(
                    ABTestEvent.experiment_id == experiment_id,
                    ABTestEvent.group == group
                ).count()
                group_counts[group] = count
            
            # 总用户数
            total_users = db.query(ABTestGroupAssignment).filter(
                ABTestGroupAssignment.experiment_id == experiment_id
            ).count()
            
            # 各组用户数
            user_counts = {}
            for (group,) in groups:
                count = db.query(ABTestGroupAssignment).filter(
                    ABTestGroupAssignment.experiment_id == experiment_id,
                    ABTestGroupAssignment.group == group
                ).count()
                user_counts[group] = count
        
        return {
            "experiment_id": experiment_id,
            "total_events": total_events,
            "total_users": total_users,
            "group_event_counts": group_counts,
            "group_user_counts": user_counts
        }
    
    except Exception as e:
        logger.error(f"获取实验统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

