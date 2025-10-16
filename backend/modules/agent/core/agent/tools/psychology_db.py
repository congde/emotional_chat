"""
Psychology DB - 心理资源数据库

提供心理健康相关资源：
- 文章
- 视频
- 自助练习
- 专业咨询信息
"""

from typing import List, Dict, Any, Optional


class PsychologyDB:
    """心理资源数据库"""
    
    def __init__(self):
        """初始化资源数据库"""
        self.resources = self._init_resources()
    
    def _init_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """初始化资源库"""
        return {
            "articles": [
                {
                    "id": "art_001",
                    "title": "如何应对焦虑情绪",
                    "category": "anxiety",
                    "difficulty": "beginner",
                    "url": "https://example.com/articles/anxiety-management",
                    "summary": "了解焦虑的本质，学习实用的应对技巧",
                    "tags": ["焦虑", "自我调节", "认知行为"],
                    "read_time": 5
                },
                {
                    "id": "art_002",
                    "title": "走出抑郁的第一步",
                    "category": "depression",
                    "difficulty": "beginner",
                    "url": "https://example.com/articles/depression-first-step",
                    "summary": "认识抑郁，迈出改变的第一步",
                    "tags": ["抑郁", "自助", "行动"],
                    "read_time": 8
                },
                {
                    "id": "art_003",
                    "title": "正念冥想入门指南",
                    "category": "mindfulness",
                    "difficulty": "beginner",
                    "url": "https://example.com/articles/mindfulness-guide",
                    "summary": "正念冥想的基础知识和练习方法",
                    "tags": ["正念", "冥想", "练习"],
                    "read_time": 10
                },
                {
                    "id": "art_004",
                    "title": "改善睡眠质量的科学方法",
                    "category": "sleep",
                    "difficulty": "beginner",
                    "url": "https://example.com/articles/sleep-improvement",
                    "summary": "基于科学研究的睡眠改善策略",
                    "tags": ["睡眠", "健康", "习惯"],
                    "read_time": 7
                }
            ],
            "videos": [
                {
                    "id": "vid_001",
                    "title": "5分钟焦虑缓解练习",
                    "category": "anxiety",
                    "duration": 5,
                    "url": "https://example.com/videos/anxiety-relief-5min",
                    "description": "快速有效的焦虑缓解技巧演示",
                    "tags": ["焦虑", "练习", "视频教程"]
                },
                {
                    "id": "vid_002",
                    "title": "渐进式肌肉放松法",
                    "category": "relaxation",
                    "duration": 15,
                    "url": "https://example.com/videos/progressive-relaxation",
                    "description": "完整的渐进式肌肉放松练习",
                    "tags": ["放松", "练习", "身体"]
                }
            ],
            "exercises": [
                {
                    "id": "ex_001",
                    "title": "情绪日记",
                    "category": "emotional_awareness",
                    "type": "journal",
                    "description": "通过记录情绪提高自我觉察",
                    "steps": [
                        "选择一个安静的时间",
                        "记录当天的情绪状态",
                        "描述触发情绪的事件",
                        "反思自己的反应",
                        "思考更好的应对方式"
                    ],
                    "frequency": "daily",
                    "duration": 10
                },
                {
                    "id": "ex_002",
                    "title": "三好练习",
                    "category": "positive_psychology",
                    "type": "reflection",
                    "description": "每天记录三件好事，培养积极心态",
                    "steps": [
                        "回顾一天中发生的事",
                        "找出三件让你感到愉快的事",
                        "写下每件事的细节",
                        "思考为什么它让你开心",
                        "感恩这些美好时刻"
                    ],
                    "frequency": "daily",
                    "duration": 5
                },
                {
                    "id": "ex_003",
                    "title": "呼吸觉察练习",
                    "category": "mindfulness",
                    "type": "meditation",
                    "description": "通过专注呼吸培养正念",
                    "steps": [
                        "找一个舒适的姿势坐下",
                        "闭上眼睛或半闭",
                        "将注意力放在呼吸上",
                        "观察呼吸的自然节奏",
                        "当思绪飘走时，温柔地带回"
                    ],
                    "frequency": "daily",
                    "duration": 10
                }
            ],
            "crisis_resources": [
                {
                    "id": "crisis_001",
                    "type": "hotline",
                    "name": "心理危机热线",
                    "phone": "400-161-9995",
                    "available": "24/7",
                    "description": "提供24小时心理危机干预服务"
                },
                {
                    "id": "crisis_002",
                    "type": "online_counseling",
                    "name": "在线心理咨询",
                    "url": "https://example.com/online-counseling",
                    "available": "9:00-21:00",
                    "description": "专业心理咨询师在线服务"
                }
            ]
        }
    
    def search_resources(
        self,
        category: Optional[str] = None,
        resource_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索资源
        
        Args:
            category: 分类（anxiety/depression/sleep等）
            resource_type: 资源类型（articles/videos/exercises）
            tags: 标签列表
            difficulty: 难度（beginner/intermediate/advanced）
            
        Returns:
            匹配的资源列表
        """
        results = []
        
        # 确定搜索范围
        if resource_type:
            search_types = [resource_type] if resource_type in self.resources else []
        else:
            search_types = ["articles", "videos", "exercises"]
        
        # 搜索
        for res_type in search_types:
            for resource in self.resources[res_type]:
                # 分类过滤
                if category and resource.get("category") != category:
                    continue
                
                # 难度过滤
                if difficulty and resource.get("difficulty") != difficulty:
                    continue
                
                # 标签过滤
                if tags:
                    resource_tags = set(resource.get("tags", []))
                    if not any(tag in resource_tags for tag in tags):
                        continue
                
                results.append({
                    **resource,
                    "resource_type": res_type
                })
        
        return results
    
    def get_recommendation(
        self,
        user_situation: str,
        emotion: str,
        resource_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        根据用户情况推荐资源
        
        Args:
            user_situation: 用户情况描述
            emotion: 情绪状态
            resource_type: 资源类型限制
            
        Returns:
            推荐资源列表
        """
        # 情绪到分类的映射
        emotion_category_map = {
            "焦虑": "anxiety",
            "抑郁": "depression",
            "难过": "depression",
            "压力": "anxiety",
            "失眠": "sleep",
            "愤怒": "anger_management"
        }
        
        category = emotion_category_map.get(emotion)
        
        # 根据情况调整推荐类型
        if "睡不好" in user_situation or "失眠" in user_situation:
            category = "sleep"
        elif "工作" in user_situation or "压力" in user_situation:
            category = "anxiety"
        
        # 搜索相关资源
        results = self.search_resources(
            category=category,
            resource_type=resource_type
        )
        
        # 优先推荐初级资源
        beginner_resources = [r for r in results if r.get("difficulty") == "beginner"]
        if beginner_resources:
            return beginner_resources[:3]
        
        return results[:3]
    
    def get_exercise_plan(
        self,
        goal: str,
        duration: int = 7
    ) -> Dict[str, Any]:
        """
        获取练习计划
        
        Args:
            goal: 目标（improve_mood/reduce_anxiety/better_sleep）
            duration: 计划天数
            
        Returns:
            练习计划
        """
        # 目标到练习的映射
        goal_exercise_map = {
            "improve_mood": ["ex_002", "ex_001"],  # 三好练习 + 情绪日记
            "reduce_anxiety": ["ex_003", "ex_001"],  # 呼吸练习 + 情绪日记
            "better_sleep": ["ex_003"],  # 呼吸练习
            "emotional_awareness": ["ex_001"]  # 情绪日记
        }
        
        exercise_ids = goal_exercise_map.get(goal, ["ex_001"])
        
        # 获取练习详情
        exercises = []
        for ex_id in exercise_ids:
            for exercise in self.resources["exercises"]:
                if exercise["id"] == ex_id:
                    exercises.append(exercise)
        
        # 生成计划
        plan = {
            "goal": goal,
            "duration": duration,
            "exercises": exercises,
            "schedule": self._generate_schedule(exercises, duration)
        }
        
        return plan
    
    def _generate_schedule(
        self,
        exercises: List[Dict[str, Any]],
        duration: int
    ) -> List[Dict[str, Any]]:
        """生成练习时间表"""
        from datetime import datetime, timedelta
        
        schedule = []
        start_date = datetime.now()
        
        for day in range(duration):
            date = start_date + timedelta(days=day)
            
            day_schedule = {
                "date": date.strftime("%Y-%m-%d"),
                "day": day + 1,
                "exercises": []
            }
            
            # 每天安排所有练习
            for exercise in exercises:
                day_schedule["exercises"].append({
                    "title": exercise["title"],
                    "duration": exercise["duration"],
                    "type": exercise["type"]
                })
            
            schedule.append(day_schedule)
        
        return schedule
    
    def get_crisis_resources(self) -> List[Dict[str, Any]]:
        """获取危机干预资源"""
        return self.resources["crisis_resources"]


# 单例模式
_psychology_db_instance = None

def get_psychology_db() -> PsychologyDB:
    """获取全局PsychologyDB实例"""
    global _psychology_db_instance
    if _psychology_db_instance is None:
        _psychology_db_instance = PsychologyDB()
    return _psychology_db_instance

