"""
Scheduler Service - 定时提醒服务

提供定时任务功能：
- 设置提醒
- 取消提醒
- 查询提醒
- 回访任务管理
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class ReminderStatus(Enum):
    """提醒状态"""
    SCHEDULED = "scheduled"     # 已安排
    COMPLETED = "completed"     # 已完成
    CANCELLED = "cancelled"     # 已取消
    EXPIRED = "expired"         # 已过期


class ReminderType(Enum):
    """提醒类型"""
    ONE_TIME = "one_time"       # 一次性
    DAILY = "daily"             # 每天
    WEEKLY = "weekly"           # 每周
    CUSTOM = "custom"           # 自定义


class SchedulerService:
    """定时提醒服务"""
    
    def __init__(self):
        """初始化调度服务"""
        # 简化实现：使用内存存储
        # 实际应该使用APScheduler或Celery
        self.reminders = {}
        self.reminder_counter = 0
    
    def create_reminder(
        self,
        user_id: str,
        content: str,
        schedule_time: datetime,
        reminder_type: ReminderType = ReminderType.ONE_TIME,
        repeat_interval: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        创建提醒
        
        Args:
            user_id: 用户ID
            content: 提醒内容
            schedule_time: 提醒时间
            reminder_type: 提醒类型
            repeat_interval: 重复间隔（天）
            metadata: 额外信息
            
        Returns:
            提醒ID
        """
        self.reminder_counter += 1
        reminder_id = f"reminder_{self.reminder_counter}"
        
        reminder = {
            "id": reminder_id,
            "user_id": user_id,
            "content": content,
            "schedule_time": schedule_time,
            "reminder_type": reminder_type.value,
            "repeat_interval": repeat_interval,
            "status": ReminderStatus.SCHEDULED.value,
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        if user_id not in self.reminders:
            self.reminders[user_id] = []
        
        self.reminders[user_id].append(reminder)
        
        return reminder_id
    
    def get_reminder(
        self,
        user_id: str,
        reminder_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取提醒详情
        
        Args:
            user_id: 用户ID
            reminder_id: 提醒ID
            
        Returns:
            提醒信息
        """
        user_reminders = self.reminders.get(user_id, [])
        
        for reminder in user_reminders:
            if reminder["id"] == reminder_id:
                return reminder
        
        return None
    
    def get_reminders(
        self,
        user_id: str,
        status: Optional[ReminderStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        获取用户的提醒列表
        
        Args:
            user_id: 用户ID
            status: 状态过滤
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            提醒列表
        """
        user_reminders = self.reminders.get(user_id, [])
        
        # 过滤
        filtered = []
        for reminder in user_reminders:
            # 状态过滤
            if status and reminder["status"] != status.value:
                continue
            
            # 日期过滤
            schedule_time = reminder["schedule_time"]
            if start_date and schedule_time < start_date:
                continue
            if end_date and schedule_time > end_date:
                continue
            
            filtered.append(reminder)
        
        # 按时间排序
        filtered.sort(key=lambda x: x["schedule_time"])
        
        return filtered
    
    def get_upcoming_reminders(
        self,
        user_id: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        获取即将到来的提醒
        
        Args:
            user_id: 用户ID
            hours: 未来几小时
            
        Returns:
            提醒列表
        """
        now = datetime.now()
        end_time = now + timedelta(hours=hours)
        
        return self.get_reminders(
            user_id=user_id,
            status=ReminderStatus.SCHEDULED,
            start_date=now,
            end_date=end_time
        )
    
    def cancel_reminder(
        self,
        user_id: str,
        reminder_id: str
    ) -> bool:
        """
        取消提醒
        
        Args:
            user_id: 用户ID
            reminder_id: 提醒ID
            
        Returns:
            是否成功取消
        """
        user_reminders = self.reminders.get(user_id, [])
        
        for reminder in user_reminders:
            if reminder["id"] == reminder_id:
                reminder["status"] = ReminderStatus.CANCELLED.value
                reminder["updated_at"] = datetime.now()
                return True
        
        return False
    
    def complete_reminder(
        self,
        user_id: str,
        reminder_id: str
    ) -> bool:
        """
        完成提醒
        
        Args:
            user_id: 用户ID
            reminder_id: 提醒ID
            
        Returns:
            是否成功完成
        """
        user_reminders = self.reminders.get(user_id, [])
        
        for reminder in user_reminders:
            if reminder["id"] == reminder_id:
                reminder["status"] = ReminderStatus.COMPLETED.value
                reminder["updated_at"] = datetime.now()
                
                # 如果是重复提醒，创建下一次
                if reminder["reminder_type"] != ReminderType.ONE_TIME.value:
                    self._schedule_next_reminder(reminder)
                
                return True
        
        return False
    
    def _schedule_next_reminder(self, reminder: Dict[str, Any]):
        """安排下一次提醒"""
        reminder_type = reminder["reminder_type"]
        current_time = reminder["schedule_time"]
        
        if reminder_type == ReminderType.DAILY.value:
            next_time = current_time + timedelta(days=1)
        elif reminder_type == ReminderType.WEEKLY.value:
            next_time = current_time + timedelta(weeks=1)
        elif reminder_type == ReminderType.CUSTOM.value:
            interval = reminder.get("repeat_interval", 1)
            next_time = current_time + timedelta(days=interval)
        else:
            return
        
        # 创建新提醒
        self.create_reminder(
            user_id=reminder["user_id"],
            content=reminder["content"],
            schedule_time=next_time,
            reminder_type=ReminderType(reminder_type),
            repeat_interval=reminder.get("repeat_interval"),
            metadata=reminder.get("metadata")
        )
    
    def check_due_reminders(self) -> List[Dict[str, Any]]:
        """
        检查到期的提醒
        
        Returns:
            到期提醒列表
        """
        now = datetime.now()
        due_reminders = []
        
        for user_id, user_reminders in self.reminders.items():
            for reminder in user_reminders:
                if (reminder["status"] == ReminderStatus.SCHEDULED.value and
                    reminder["schedule_time"] <= now):
                    due_reminders.append(reminder)
        
        return due_reminders
    
    def update_reminder(
        self,
        user_id: str,
        reminder_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新提醒
        
        Args:
            user_id: 用户ID
            reminder_id: 提醒ID
            updates: 更新内容
            
        Returns:
            是否成功更新
        """
        user_reminders = self.reminders.get(user_id, [])
        
        for reminder in user_reminders:
            if reminder["id"] == reminder_id:
                reminder.update(updates)
                reminder["updated_at"] = datetime.now()
                return True
        
        return False


# 单例模式
_scheduler_service_instance = None

def get_scheduler_service() -> SchedulerService:
    """获取全局SchedulerService实例"""
    global _scheduler_service_instance
    if _scheduler_service_instance is None:
        _scheduler_service_instance = SchedulerService()
    return _scheduler_service_instance

