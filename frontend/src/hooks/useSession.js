import { useState, useEffect, useRef, useCallback } from 'react';
import ChatAPI from '../services/ChatAPI';

export const useSession = (currentUserId) => {
  const [sessionId, setSessionId] = useState(null);
  const [historySessions, setHistorySessions] = useState([]);
  
  const isLoadingHistoryRef = useRef(false);
  const currentLoadingSessionIdRef = useRef(null);
  const loadedSessionIdRef = useRef(null);

  // 会话ID改变时保存到localStorage
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('emotional_chat_current_session', sessionId);
    }
  }, [sessionId]);

  // 加载历史会话
  const loadHistorySessions = useCallback(async () => {
    try {
      const response = await ChatAPI.getUserSessions(currentUserId);
      setHistorySessions(response.sessions || []);
    } catch (error) {
      console.error('加载历史会话失败:', error);
    }
  }, [currentUserId]);

  useEffect(() => {
    loadHistorySessions();
  }, [loadHistorySessions]);

  const loadSessionHistory = useCallback(async (targetSessionId, setMessages, setSuggestions) => {
    // 防止重复调用
    if (isLoadingHistoryRef.current && currentLoadingSessionIdRef.current === targetSessionId) {
      return;
    }
    
    if (targetSessionId === loadedSessionIdRef.current) {
      return;
    }
    
    isLoadingHistoryRef.current = true;
    currentLoadingSessionIdRef.current = targetSessionId;
    
    try {
      const response = await ChatAPI.getSessionHistory(targetSessionId);
      
      if (!response || !response.messages) {
        setMessages([]);
        return;
      }
      
      // 处理消息去重和排序
      const messageMap = new Map();
      const contentKeyMap = new Map();
      
      response.messages.forEach((msg, index) => {
        const dbId = msg.id;
        const contentKey = `${msg.role}_${msg.content}`;
        
        if (dbId) {
          if (messageMap.has(dbId) || contentKeyMap.has(contentKey)) {
            return;
          }
          
          const messageObj = {
            id: `history_${targetSessionId}_${dbId}_${msg.timestamp}`,
            role: msg.role,
            content: msg.content,
            emotion: msg.emotion,
            timestamp: new Date(msg.timestamp),
            dbId: dbId,
            isHistory: true
          };
          
          messageMap.set(dbId, messageObj);
          contentKeyMap.set(contentKey, messageObj);
        } else {
          if (contentKeyMap.has(contentKey)) {
            return;
          }
          
          const messageObj = {
            id: `history_${targetSessionId}_${index}_${msg.timestamp}`,
            role: msg.role,
            content: msg.content,
            emotion: msg.emotion,
            timestamp: new Date(msg.timestamp),
            dbId: null,
            isHistory: true
          };
          
          messageMap.set(`no_id_${index}`, messageObj);
          contentKeyMap.set(contentKey, messageObj);
        }
      });
      
      const sessionMessages = Array.from(messageMap.values());
      
      sessionMessages.sort((a, b) => {
        const timeDiff = a.timestamp - b.timestamp;
        if (timeDiff !== 0) return timeDiff;
        if (a.dbId !== undefined && b.dbId !== undefined) {
          return a.dbId - b.dbId;
        }
        if (a.role === 'user' && b.role === 'assistant') return -1;
        if (a.role === 'assistant' && b.role === 'user') return 1;
        return 0;
      });
      
      setMessages(sessionMessages);
      setSessionId(targetSessionId);
      loadedSessionIdRef.current = targetSessionId;
      setSuggestions([]);
    } catch (error) {
      console.error('加载会话历史失败:', error);
    } finally {
      isLoadingHistoryRef.current = false;
      currentLoadingSessionIdRef.current = null;
    }
  }, []);

  const deleteConversation = useCallback(async (targetSessionId, currentSessionId, setMessages, setSessionId, setSuggestions) => {
    if (window.confirm('确定要删除这个对话吗？此操作无法撤销。')) {
      try {
        await ChatAPI.deleteSession(targetSessionId);
        
        if (targetSessionId === currentSessionId) {
          setMessages([]);
          setSessionId(null);
          loadedSessionIdRef.current = null;
          setSuggestions([]);
        }
        
        loadHistorySessions();
      } catch (error) {
        console.error('删除对话失败:', error);
        alert('删除对话失败，请稍后重试');
      }
    }
  }, [loadHistorySessions]);

  const startNewChat = useCallback((setMessages, setSessionId, setSuggestions, setAttachments, setDetectedURLs) => {
    setMessages([]);
    setSessionId(null);
    loadedSessionIdRef.current = null;
    setSuggestions([]);
    setAttachments([]);
    setDetectedURLs([]);
  }, []);

  return {
    sessionId,
    setSessionId,
    historySessions,
    loadHistorySessions,
    loadSessionHistory,
    deleteConversation,
    startNewChat
  };
};

