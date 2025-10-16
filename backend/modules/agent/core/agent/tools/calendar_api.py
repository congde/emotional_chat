"""
Calendar API - 日历服务

提供日历相关功能：
- 查询事件
- 创建事件
- 更新事件
- 删除事件
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class CalendarAPI:
    """日历API服务"""
    
    def __init__(self):
        """初始化日历服务"""
        # 简化实现：使用内存存储
        # 实际应该对接Google Calendar、Outlook等API
        self.events_db = {}
    
    def get_events(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户日历事件
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            事件列表
        """
        user_events = self.events_db.get(user_id, [])
        
        # 日期过滤
        if start_date or end_date:
            filtered_events = []
            for event in user_events:
                event_date = datetime.fromisoformat(event["date"])
                
                if start_date and event_date < start_date:
                    continue
                if end_date and event_date > end_date:
                    continue
                
                filtered_events.append(event)
            
            return filtered_events
        
        return user_events
    
    def create_event(
        self,
        user_id: str,
        title: str,
        date: str,
        time: str,
        description: Optional[str] = None,
        event_type: str = "personal"
    ) -> Dict[str, Any]:
        """
        创建日历事件
        
        Args:
            user_id: 用户ID
            title: 事件标题
            date: 日期（YYYY-MM-DD）
            time: 时间（HH:MM）
            description: 描述
            event_type: 事件类型（work/personal/health）
            
        Returns:
            创建的事件
        """
        event = {
            "id": f"event_{len(self.events_db.get(user_id, []))}",
            "title": title,
            "date": date,
            "time": time,
            "description": description,
            "type": event_type,
            "created_at": datetime.now().isoformat()
        }
        
        if user_id not in self.events_db:
            self.events_db[user_id] = []
        
        self.events_db[user_id].append(event)
        
        return event
    
    def update_event(
        self,
        user_id: str,
        event_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新日历事件
        
        Args:
            user_id: 用户ID
            event_id: 事件ID
            updates: 更新内容
            
        Returns:
            更新后的事件
        """
        user_events = self.events_db.get(user_id, [])
        
        for event in user_events:
            if event["id"] == event_id:
                event.update(updates)
                event["updated_at"] = datetime.now().isoformat()
                return event
        
        return None
    
    def delete_event(
        self,
        user_id: str,
        event_id: str
    ) -> bool:
        """
        删除日历事件
        
        Args:
            user_id: 用户ID
            event_id: 事件ID
            
        Returns:
            是否成功删除
        """
        user_events = self.events_db.get(user_id, [])
        
        for i, event in enumerate(user_events):
            if event["id"] == event_id:
                user_events.pop(i)
                return True
        
        return False
    
    def get_upcoming_events(
        self,
        user_id: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        获取即将到来的事件
        
        Args:
            user_id: 用户ID
            days: 未来几天
            
        Returns:
            事件列表
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        return self.get_events(user_id, start_date, end_date)
    
    def suggest_time_slot(
        self,
        user_id: str,
        date: str,
        duration: int = 60
    ) -> List[str]:
        """
        建议可用时间段
        
        Args:
            user_id: 用户ID
            date: 日期
            duration: 持续时间（分钟）
            
        Returns:
            可用时间段列表
        """
        # 获取当天事件
        day_events = [
            e for e in self.events_db.get(user_id, [])
            if e["date"] == date
        ]
        
        # 简化实现：返回空闲时段
        # 工作时间 9:00-18:00
        available_slots = []
        
        busy_times = set([e["time"] for e in day_events])
        
        for hour in range(9, 18):
            time_slot = f"{hour:02d}:00"
            if time_slot not in busy_times:
                available_slots.append(time_slot)
        
        return available_slots[:3]  # 返回前3个可用时段


# 单例模式
_calendar_api_instance = None

def get_calendar_api() -> CalendarAPI:
    """获取全局CalendarAPI实例"""
    global _calendar_api_instance
    if _calendar_api_instance is None:
        _calendar_api_instance = CalendarAPI()
    return _calendar_api_instance

