#!/usr/bin/env python3
"""
上下文服务层
负责组装和管理对话上下文
集成上下文腐烂（Context Rot）解决方案
"""

from typing import Dict, List, Optional, Any
from backend.context_assembler import ContextAssembler, UserProfile
from backend.services.memory_service import MemoryService
from backend.services.context_rot_solver import ContextRotSolver, ContextRotThreshold
from backend.services.context_retrieval_optimizer import ContextRetrievalOptimizer
from backend.database import DatabaseManager


class ContextService:
    """上下文服务 - 管理对话上下文"""
    
    def __init__(
        self,
        memory_service: Optional[MemoryService] = None,
        enable_rot_solver: bool = True,
        rot_threshold: int = ContextRotThreshold.SAFE.value
    ):
        """
        初始化上下文服务
        
        Args:
            memory_service: 记忆服务
            enable_rot_solver: 是否启用上下文腐烂解决方案
            rot_threshold: 上下文腐烂阈值（默认128K tokens）
        """
        self.assembler = ContextAssembler()
        self.memory_service = memory_service or MemoryService()
        self.enable_rot_solver = enable_rot_solver
        
        # 初始化上下文腐烂解决方案
        if self.enable_rot_solver:
            self.rot_solver = ContextRotSolver(pre_rot_threshold=rot_threshold)
            self.retrieval_optimizer = ContextRetrievalOptimizer()
        else:
            self.rot_solver = None
            self.retrieval_optimizer = None
    
    async def build_context(
        self,
        user_id: str,
        session_id: str,
        current_message: str,
        emotion: Optional[str] = None,
        emotion_intensity: Optional[float] = None,
        auto_reduce: bool = True
    ) -> Dict[str, Any]:
        """
        构建完整的对话上下文
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            current_message: 当前用户消息
            emotion: 当前情绪
            emotion_intensity: 情绪强度
            auto_reduce: 是否自动缩减上下文（防止腐烂）
            
        Returns:
            完整的上下文数据（可能已缩减）
        """
        # 获取对话历史
        chat_history = await self._get_chat_history(session_id)
        
        # 组装上下文
        context = self.assembler.assemble_context(
            user_id=user_id,
            session_id=session_id,
            current_message=current_message,
            chat_history=chat_history,
            emotion=emotion,
            emotion_intensity=emotion_intensity
        )
        
        # 应用上下文腐烂解决方案
        if self.enable_rot_solver and auto_reduce:
            context = self._apply_context_optimization(context, session_id)
        
        return context
    
    def _apply_context_optimization(
        self,
        context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        应用上下文优化（压缩/摘要）
        
        Args:
            context: 原始上下文
            session_id: 会话ID
            
        Returns:
            优化后的上下文
        """
        if not self.rot_solver:
            return context
        
        # 检查上下文状态
        status = self.rot_solver.get_context_status(context)
        
        # 如果超过阈值，进行缩减
        if status["status"] in ["caution", "warning", "critical"]:
            # 执行缩减
            reduced_context = self.rot_solver.reduce_context(
                context,
                preserve_recent_turns=5  # 保留最近5轮完整对话
            )
            
            # 记录优化信息
            reduced_context["optimization"] = {
                "original_tokens": status["token_count"],
                "reduced_tokens": self.rot_solver.estimate_tokens(reduced_context),
                "status": status["status"],
                "recommendation": status["recommendation"],
                "optimized_at": context.get("metadata", {}).get("timestamp")
            }
            
            return reduced_context
        
        return context
    
    async def build_prompt(
        self,
        context: Dict[str, Any],
        system_prompt: str
    ) -> str:
        """
        根据上下文构建完整的prompt
        
        Args:
            context: 上下文数据
            system_prompt: 系统prompt
            
        Returns:
            完整的prompt文本
        """
        return self.assembler.build_prompt_context(context, system_prompt)
    
    async def _get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """获取对话历史"""
        try:
            with DatabaseManager() as db:
                messages = db.get_session_messages(session_id, limit=limit)
                
                return [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "emotion": msg.emotion,
                        "timestamp": msg.created_at.isoformat() if msg.created_at else None
                    }
                    for msg in reversed(messages)  # 按时间正序
                ]
        except Exception as e:
            print(f"获取对话历史失败: {e}")
            return []
    
    async def get_user_profile(self, user_id: str) -> UserProfile:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像对象
        """
        return self.assembler.get_user_profile(user_id)
    
    async def update_user_profile(
        self,
        user_id: str,
        updates: Dict[str, Any]
    ) -> UserProfile:
        """
        更新用户画像
        
        Args:
            user_id: 用户ID
            updates: 更新的字段
            
        Returns:
            更新后的用户画像
        """
        return self.assembler.update_user_profile(user_id, updates)
    
    async def get_context_summary(self, context: Dict[str, Any]) -> str:
        """
        获取上下文摘要
        
        Args:
            context: 上下文数据
            
        Returns:
            摘要文本
        """
        return self.assembler.generate_context_summary(context)
    
    def get_context_status(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取上下文状态报告（包括token计数和腐烂风险）
        
        Args:
            context: 上下文数据
            
        Returns:
            状态报告
        """
        if not self.rot_solver:
            return {"status": "rot_solver_disabled"}
        
        return self.rot_solver.get_context_status(context)
    
    async def offload_context(
        self,
        context: Dict[str, Any],
        session_id: str
    ) -> Dict[str, Any]:
        """
        将上下文卸载到文件系统
        
        Args:
            context: 完整上下文
            session_id: 会话ID
            
        Returns:
            卸载后的精简上下文
        """
        if not self.rot_solver:
            return context
        
        offloaded, file_path = self.rot_solver.offload_to_file(context, session_id)
        return offloaded
    
    async def load_offloaded_context(self, file_path: str) -> Dict[str, Any]:
        """
        从文件系统加载已卸载的上下文
        
        Args:
            file_path: 文件路径
            
        Returns:
            完整的上下文数据
        """
        if not self.rot_solver:
            return {}
        
        return self.rot_solver.load_from_file(file_path)
    
    async def retrieve_relevant_context(
        self,
        query: str,
        context_type: Optional[str] = None,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        检索相关上下文（使用优化的检索策略）
        
        Args:
            query: 查询文本
            context_type: 上下文类型
            max_results: 最大结果数
            
        Returns:
            相关上下文列表
        """
        if not self.retrieval_optimizer:
            return []
        
        return self.retrieval_optimizer.retrieve_relevant_context(
            query,
            context_type,
            max_results
        )

