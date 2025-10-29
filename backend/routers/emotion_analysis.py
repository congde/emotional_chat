#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
情感分析API路由
提供情感分析、趋势分析和情绪报告的HTTP接口
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from backend.services.advanced_sentiment_analyzer import get_analyzer
from backend.services.emotion_trend_analyzer import EmotionTrendAnalyzer

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/api/emotion",
    tags=["emotion_analysis"]
)

# 初始化服务
sentiment_analyzer = get_analyzer(use_transformers=False)
trend_analyzer = EmotionTrendAnalyzer()


# ============================================
# 请求/响应模型
# ============================================

class SentimentAnalysisRequest(BaseModel):
    """情感分析请求"""
    text: str = Field(..., description="要分析的文本", min_length=1, max_length=1000)
    user_id: Optional[str] = Field(None, description="用户ID（用于趋势追踪）")


class SentimentAnalysisResponse(BaseModel):
    """情感分析响应"""
    emotion: str = Field(..., description="检测到的情绪")
    confidence: float = Field(..., description="置信度（0-1）")
    intensity: float = Field(..., description="强度（0-10）")
    polarity: int = Field(..., description="极性（-1/0/1）")
    emotion_scores: Dict[str, float] = Field({}, description="多维度情绪得分")
    keywords: list = Field([], description="关键词")
    suggestions: list = Field([], description="回复建议")
    method: str = Field(..., description="分析方法（transformers/keywords）")


class EmotionTrendResponse(BaseModel):
    """情绪趋势响应"""
    trend: str = Field(..., description="趋势方向（improving/declining/stable）")
    average_intensity: float = Field(..., description="平均强度")
    dominant_emotion: str = Field(..., description="主导情绪")
    emotion_distribution: Dict[str, float] = Field({}, description="情绪分布")
    warning: Optional[str] = Field(None, description="预警信息")
    sample_size: int = Field(..., description="样本数量")


class EmotionReportResponse(BaseModel):
    """情绪报告响应"""
    user_id: str
    analysis_period_days: int
    sample_size: int
    trend_analysis: Dict[str, Any]
    emotion_profile: Dict[str, Any]
    visualization_data: Optional[Dict[str, Any]] = None


# ============================================
# API端点
# ============================================

@router.post("/analyze", response_model=SentimentAnalysisResponse)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """
    分析文本的情感
    
    这是实时情感分析接口，可以独立使用或集成到对话流程中。
    
    **示例请求**:
    ```json
    {
        "text": "今天好累啊，工作压力太大了",
        "user_id": "user_123"
    }
    ```
    
    **返回**:
    - emotion: 情绪类型（happy/sad/angry/anxious等）
    - confidence: 置信度（0-1）
    - intensity: 强度（0-10）
    - polarity: 极性（-1=负面, 0=中性, 1=正面）
    - emotion_scores: 多维度情绪得分
    - keywords: 提取的关键词
    - suggestions: AI回复建议
    """
    try:
        result = sentiment_analyzer.analyze(
            text=request.text,
            user_id=request.user_id
        )
        
        return SentimentAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"情感分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"情感分析失败: {str(e)}")


@router.get("/trend/{user_id}", response_model=EmotionTrendResponse)
async def get_emotion_trend(
    user_id: str,
    window: int = Query(10, ge=2, le=100, description="分析窗口大小（最近N条消息）")
):
    """
    获取用户的情绪趋势
    
    基于最近N条消息分析用户的情绪趋势。
    
    **参数**:
    - user_id: 用户ID
    - window: 分析窗口大小（默认10条）
    
    **返回**:
    - trend: 趋势方向（improving/declining/stable）
    - average_intensity: 平均强度
    - dominant_emotion: 主导情绪
    - emotion_distribution: 情绪分布
    - warning: 风险预警（如果有）
    
    **示例**:
    ```
    GET /api/emotion/trend/user_123?window=10
    ```
    """
    try:
        trend = sentiment_analyzer.get_emotion_trend(user_id, window=window)
        
        if trend.get("trend") == "unknown":
            raise HTTPException(status_code=404, detail="用户情绪数据不足")
        
        return EmotionTrendResponse(**trend)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"趋势分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"趋势分析失败: {str(e)}")


@router.get("/report/{user_id}", response_model=EmotionReportResponse)
async def get_emotion_report(
    user_id: str,
    days: int = Query(7, ge=1, le=90, description="分析天数"),
    include_visualization: bool = Query(True, description="是否包含可视化数据")
):
    """
    生成用户情绪报告
    
    生成包含趋势分析、多维度画像和可视化数据的完整情绪报告。
    
    **参数**:
    - user_id: 用户ID
    - days: 分析天数（1-90天）
    - include_visualization: 是否包含可视化数据
    
    **返回**:
    - trend_analysis: 趋势分析（包含风险评估、模式识别等）
    - emotion_profile: 多维度情绪画像（6个维度）
    - visualization_data: 可视化数据（时间线、饼图、柱状图等）
    
    **示例**:
    ```
    GET /api/emotion/report/user_123?days=7&include_visualization=true
    ```
    
    **可视化数据格式**:
    - timeline: 时间序列数据（情绪强度曲线）
    - pie_chart: 饼图数据（情绪分布）
    - bar_chart: 柱状图数据（每日平均强度）
    - heatmap: 热力图数据（情绪转换矩阵）
    """
    try:
        # 1. 获取趋势分析
        trend_analysis = trend_analyzer.analyze_user_emotion_trend(
            user_id=user_id,
            days=days,
            include_visualization_data=include_visualization
        )
        
        if trend_analysis["sample_size"] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"用户 {user_id} 在过去 {days} 天内没有足够的数据"
            )
        
        # 2. 获取多维度情绪画像
        emotion_profile = trend_analyzer.get_multi_dimensional_emotion_profile(
            user_id=user_id,
            days=min(days * 2, 30)
        )
        
        return EmotionReportResponse(
            user_id=user_id,
            analysis_period_days=days,
            sample_size=trend_analysis["sample_size"],
            trend_analysis=trend_analysis,
            emotion_profile=emotion_profile,
            visualization_data=trend_analysis.get("visualization_data") if include_visualization else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成情绪报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成情绪报告失败: {str(e)}")


@router.get("/profile/{user_id}")
async def get_emotion_profile(
    user_id: str,
    days: int = Query(30, ge=7, le=90, description="分析天数")
):
    """
    获取用户的多维度情绪画像
    
    生成包含6个维度的情绪特征画像：
    1. 情绪稳定性
    2. 情绪复杂度
    3. 积极性指数
    4. 压力指数
    5. 社交连接
    6. 情绪弹性
    
    **参数**:
    - user_id: 用户ID
    - days: 分析天数（建议30天）
    
    **返回示例**:
    ```json
    {
        "user_id": "user_123",
        "analysis_period_days": 30,
        "sample_size": 45,
        "dimensions": {
            "stability": {"score": 0.65, "level": "中", "description": "情绪稳定性"},
            "complexity": {"score": 0.60, "unique_emotions": 6},
            "positivity": {"score": 0.35, "level": "中"},
            "stress": {"score": 0.45, "level": "高"},
            "social_connectedness": {"score": 0.55, "level": "中"},
            "resilience": {"score": 0.70, "level": "高"}
        },
        "overall_wellbeing_score": 0.58,
        "key_characteristics": ["压力较高", "情绪恢复能力强"]
    }
    ```
    """
    try:
        profile = trend_analyzer.get_multi_dimensional_emotion_profile(user_id, days)
        
        if "error" in profile:
            raise HTTPException(
                status_code=404,
                detail=profile["error"]
            )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取情绪画像失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取情绪画像失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查
    
    检查情感分析服务的状态。
    
    **返回**:
    - status: 服务状态
    - sentiment_analyzer: 情感分析器状态
    - trend_analyzer: 趋势分析器状态
    """
    return {
        "status": "healthy",
        "sentiment_analyzer": {
            "available": sentiment_analyzer is not None,
            "use_transformers": sentiment_analyzer.use_transformers if sentiment_analyzer else False
        },
        "trend_analyzer": {
            "available": trend_analyzer is not None
        }
    }


# ============================================
# 便捷端点（用于快速测试）
# ============================================

@router.post("/quick_analyze")
async def quick_analyze(text: str = Query(..., description="要分析的文本")):
    """
    快速情感分析（简化接口）
    
    **示例**:
    ```
    POST /api/emotion/quick_analyze?text=今天好开心
    ```
    
    **返回**:
    ```json
    {
        "emotion": "happy",
        "intensity": 7.5,
        "suggestion": "很高兴看到你这么开心！"
    }
    ```
    """
    try:
        result = sentiment_analyzer.analyze(text)
        
        return {
            "emotion": result["emotion"],
            "intensity": result["intensity"],
            "confidence": result["confidence"],
            "suggestion": result["suggestions"][0] if result["suggestions"] else "我在倾听。"
        }
        
    except Exception as e:
        logger.error(f"快速分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 导出路由器
# ============================================

__all__ = ["router"]

