#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个性化配置API路由
提供用户个性化配置的CRUD接口
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import logging
from typing import List, Optional

from backend.models import (
    PersonalizationConfig,
    PersonalizationUpdateRequest,
    PersonalizationResponse,
    RoleTemplate
)
from backend.database import get_db, UserPersonalization
from backend.services.prompt_composer import (
    PromptComposer,
    get_role_template,
    get_all_role_templates
)

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(
    prefix="/api/personalization",
    tags=["personalization"]
)


# ============================================
# API端点
# ============================================

@router.get("/templates", response_model=List[RoleTemplate])
async def get_role_templates():
    """
    获取所有预设角色模板
    
    返回可用的角色模板列表，用户可以基于这些模板创建个性化配置。
    
    **返回示例**:
    ```json
    [
        {
            "id": "warm_listener",
            "name": "温暖倾听者",
            "role": "温暖倾听者",
            "personality": "温暖、耐心、善于倾听",
            "description": "一个温暖的陪伴者，善于倾听，给予理解和支持",
            "icon": "❤️"
        }
    ]
    ```
    """
    try:
        templates = get_all_role_templates()
        return templates
    except Exception as e:
        logger.error(f"获取角色模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取角色模板失败: {str(e)}")


@router.get("/template/{template_id}", response_model=RoleTemplate)
async def get_template_detail(template_id: str):
    """
    获取特定角色模板的详细信息
    
    **参数**:
    - template_id: 模板ID（如 warm_listener）
    
    **返回**:
    完整的角色模板配置，包括示例回复和核心原则
    """
    try:
        template = get_role_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模板详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{user_id}")
async def get_user_config(user_id: str, db: Session = Depends(get_db)):
    """
    获取用户的个性化配置
    
    **参数**:
    - user_id: 用户ID
    
    **返回**:
    用户的完整个性化配置。如果用户没有配置，返回默认配置。
    
    **示例**:
    ```
    GET /api/personalization/config/user_123
    ```
    """
    try:
        config_db = db.query(UserPersonalization).filter(
            UserPersonalization.user_id == user_id
        ).first()
        
        if not config_db:
            # 返回默认配置
            return {
                "user_id": user_id,
                "config": {
                    "user_id": user_id,
                    "role": "温暖倾听者",
                    "role_name": "心语",
                    "personality": "温暖耐心",
                    "tone": "温和",
                    "style": "简洁",
                    "formality": 0.3,
                    "enthusiasm": 0.5,
                    "empathy_level": 0.8,
                    "humor_level": 0.3,
                    "response_length": "medium",
                    "use_emoji": False,
                    "learning_mode": True,
                    "safety_level": "standard",
                    "context_window": 10,
                    "active_role": "default"
                },
                "total_interactions": 0,
                "positive_feedbacks": 0,
                "config_version": 1,
                "is_default": True
            }
        
        # 转换数据库记录为响应格式
        config = {
            "user_id": config_db.user_id,
            "role": config_db.role,
            "role_name": config_db.role_name,
            "role_background": config_db.role_background,
            "personality": config_db.personality,
            "core_principles": json.loads(config_db.core_principles) if config_db.core_principles else None,
            "forbidden_behaviors": json.loads(config_db.forbidden_behaviors) if config_db.forbidden_behaviors else None,
            "tone": config_db.tone,
            "style": config_db.style,
            "formality": config_db.formality,
            "enthusiasm": config_db.enthusiasm,
            "empathy_level": config_db.empathy_level,
            "humor_level": config_db.humor_level,
            "response_length": config_db.response_length,
            "use_emoji": config_db.use_emoji,
            "preferred_topics": json.loads(config_db.preferred_topics) if config_db.preferred_topics else None,
            "avoided_topics": json.loads(config_db.avoided_topics) if config_db.avoided_topics else None,
            "communication_preferences": json.loads(config_db.communication_preferences) if config_db.communication_preferences else None,
            "learning_mode": config_db.learning_mode,
            "safety_level": config_db.safety_level,
            "context_window": config_db.context_window,
            "situational_roles": json.loads(config_db.situational_roles) if config_db.situational_roles else None,
            "active_role": config_db.active_role
        }
        
        return {
            "user_id": config_db.user_id,
            "config": config,
            "total_interactions": config_db.total_interactions,
            "positive_feedbacks": config_db.positive_feedbacks,
            "config_version": config_db.config_version,
            "created_at": config_db.created_at,
            "updated_at": config_db.updated_at,
            "is_default": False
        }
        
    except Exception as e:
        logger.error(f"获取用户配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/config/{user_id}")
async def create_or_update_config(
    user_id: str,
    update_data: PersonalizationUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    创建或更新用户的个性化配置
    
    **参数**:
    - user_id: 用户ID
    - update_data: 更新数据（只需提供要更新的字段）
    
    **示例请求**:
    ```json
    {
        "role": "智慧导师",
        "role_name": "智者",
        "tone": "沉稳",
        "empathy_level": 0.7,
        "use_emoji": true
    }
    ```
    
    **返回**:
    更新后的完整配置
    """
    try:
        # 查找现有配置
        config_db = db.query(UserPersonalization).filter(
            UserPersonalization.user_id == user_id
        ).first()
        
        if config_db:
            # 更新现有配置
            update_dict = update_data.dict(exclude_unset=True)
            
            for key, value in update_dict.items():
                if value is not None:
                    # JSON字段特殊处理
                    if key in ['core_principles', 'forbidden_behaviors', 'preferred_topics', 
                              'avoided_topics', 'communication_preferences', 'situational_roles']:
                        if value is not None:
                            setattr(config_db, key, json.dumps(value, ensure_ascii=False))
                    else:
                        setattr(config_db, key, value)
            
            # 增加版本号
            config_db.config_version += 1
            
        else:
            # 创建新配置
            config_data = {
                "user_id": user_id,
                "role": update_data.role or "温暖倾听者",
                "role_name": update_data.role_name or "心语",
                "role_background": update_data.role_background,
                "personality": update_data.personality or "温暖耐心",
                "tone": update_data.tone or "温和",
                "style": update_data.style or "简洁",
                "formality": update_data.formality if update_data.formality is not None else 0.3,
                "enthusiasm": update_data.enthusiasm if update_data.enthusiasm is not None else 0.5,
                "empathy_level": update_data.empathy_level if update_data.empathy_level is not None else 0.8,
                "humor_level": update_data.humor_level if update_data.humor_level is not None else 0.3,
                "response_length": update_data.response_length or "medium",
                "use_emoji": update_data.use_emoji if update_data.use_emoji is not None else False,
                "learning_mode": update_data.learning_mode if update_data.learning_mode is not None else True,
                "safety_level": update_data.safety_level or "standard",
                "context_window": update_data.context_window or 10,
                "active_role": update_data.active_role or "default"
            }
            
            # JSON字段
            if update_data.core_principles:
                config_data["core_principles"] = json.dumps(update_data.core_principles, ensure_ascii=False)
            if update_data.forbidden_behaviors:
                config_data["forbidden_behaviors"] = json.dumps(update_data.forbidden_behaviors, ensure_ascii=False)
            if update_data.preferred_topics:
                config_data["preferred_topics"] = json.dumps(update_data.preferred_topics, ensure_ascii=False)
            if update_data.avoided_topics:
                config_data["avoided_topics"] = json.dumps(update_data.avoided_topics, ensure_ascii=False)
            if update_data.communication_preferences:
                config_data["communication_preferences"] = json.dumps(update_data.communication_preferences, ensure_ascii=False)
            if update_data.situational_roles:
                config_data["situational_roles"] = json.dumps(update_data.situational_roles, ensure_ascii=False)
            
            config_db = UserPersonalization(**config_data)
            db.add(config_db)
        
        db.commit()
        db.refresh(config_db)
        
        # 返回更新后的配置（调用get_user_config）
        return await get_user_config(user_id, db)
        
    except Exception as e:
        db.rollback()
        logger.error(f"更新用户配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.post("/config/{user_id}/apply-template")
async def apply_template(
    user_id: str,
    template_id: str,
    db: Session = Depends(get_db)
):
    """
    应用角色模板到用户配置
    
    **参数**:
    - user_id: 用户ID
    - template_id: 模板ID
    
    **示例**:
    ```
    POST /api/personalization/config/user_123/apply-template?template_id=wise_mentor
    ```
    
    **返回**:
    应用模板后的完整配置
    """
    try:
        # 获取模板
        template = get_role_template(template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"模板 {template_id} 不存在")
        
        # 将模板转换为配置更新请求
        update_data = PersonalizationUpdateRequest(
            role=template["role"],
            role_name=template["name"],
            role_background=template.get("background"),
            personality=template["personality"],
            tone=template["tone"],
            style=template["style"],
            core_principles=template.get("core_principles", [])
        )
        
        # 应用配置
        return await create_or_update_config(user_id, update_data, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"应用模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"应用模板失败: {str(e)}")


@router.delete("/config/{user_id}")
async def delete_user_config(user_id: str, db: Session = Depends(get_db)):
    """
    删除用户的个性化配置（重置为默认）
    
    **参数**:
    - user_id: 用户ID
    
    **返回**:
    删除结果
    """
    try:
        config_db = db.query(UserPersonalization).filter(
            UserPersonalization.user_id == user_id
        ).first()
        
        if not config_db:
            raise HTTPException(status_code=404, detail="用户配置不存在")
        
        db.delete(config_db)
        db.commit()
        
        return {
            "success": True,
            "message": f"用户 {user_id} 的配置已重置为默认"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"删除用户配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")


@router.get("/preview/{user_id}")
async def preview_prompt(
    user_id: str,
    context: str = "用户说：今天心情不太好...",
    emotion: Optional[str] = None,
    intensity: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    预览根据当前配置生成的Prompt
    
    用于测试和调试个性化配置的效果。
    
    **参数**:
    - user_id: 用户ID
    - context: 对话上下文（默认测试文本）
    - emotion: 情绪类型（可选）
    - intensity: 情绪强度（可选）
    
    **返回**:
    生成的完整Prompt文本
    
    **示例**:
    ```
    GET /api/personalization/preview/user_123?context=今天很开心&emotion=happy&intensity=8
    ```
    """
    try:
        # 获取用户配置
        config_response = await get_user_config(user_id, db)
        config = config_response["config"]
        
        # 创建Prompt组合器
        composer = PromptComposer(config)
        
        # 构建情绪状态
        emotion_state = None
        if emotion and intensity is not None:
            emotion_state = {
                "emotion": emotion,
                "intensity": intensity
            }
        
        # 生成Prompt
        prompt = composer.compose(context=context, emotion_state=emotion_state)
        
        return {
            "user_id": user_id,
            "config_summary": composer.get_summary(),
            "prompt": prompt,
            "context": context,
            "emotion_state": emotion_state
        }
        
    except Exception as e:
        logger.error(f"预览Prompt失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览失败: {str(e)}")


@router.post("/feedback/{user_id}")
async def record_feedback(
    user_id: str,
    feedback_type: str,  # positive/negative
    db: Session = Depends(get_db)
):
    """
    记录用户对个性化配置的反馈
    
    用于学习模式下调整配置。
    
    **参数**:
    - user_id: 用户ID
    - feedback_type: 反馈类型（positive/negative）
    
    **返回**:
    更新后的统计信息
    """
    try:
        config_db = db.query(UserPersonalization).filter(
            UserPersonalization.user_id == user_id
        ).first()
        
        if not config_db:
            raise HTTPException(status_code=404, detail="用户配置不存在")
        
        # 更新统计
        config_db.total_interactions += 1
        if feedback_type == "positive":
            config_db.positive_feedbacks += 1
        
        db.commit()
        
        return {
            "user_id": user_id,
            "total_interactions": config_db.total_interactions,
            "positive_feedbacks": config_db.positive_feedbacks,
            "satisfaction_rate": (
                config_db.positive_feedbacks / config_db.total_interactions 
                if config_db.total_interactions > 0 else 0
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"记录反馈失败: {e}")
        raise HTTPException(status_code=500, detail=f"记录反馈失败: {str(e)}")


@router.get("/health")
async def health_check():
    """
    健康检查
    
    检查个性化配置服务的状态。
    """
    return {
        "status": "healthy",
        "service": "personalization",
        "available_templates": len(get_all_role_templates())
    }


# ============================================
# 导出路由器
# ============================================

__all__ = ["router"]





