import { useState, useRef, useCallback } from 'react';
import ChatAPI from '../services/ChatAPI';
import { detectURLs } from '../utils/formatters';

export const useChat = (currentUserId) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);
  const abortRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const sendMessage = useCallback(async (inputValue, attachments, setInputValue, setAttachments, setDetectedURLs, deepThinking = false) => {
    if ((!inputValue.trim() && attachments.length === 0) || isLoading) return;

    const userMessage = inputValue.trim();
    const urls = detectURLs(userMessage);
    
    // 处理检测到的URL
    let urlContents = [];
    if (urls.length > 0) {
      for (const url of urls) {
        try {
          const urlContent = await ChatAPI.parseURL({ url });
          if (urlContent) {
            urlContents.push(urlContent);
          }
        } catch (error) {
          console.error('URL解析失败:', error);
        }
      }
    }

    setInputValue('');
    setIsLoading(true);

    // 添加用户消息
    const newUserMessage = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      attachments: attachments.map(att => ({
        id: att.id,
        name: att.name,
        type: att.type,
        size: att.size
      })),
      urls: urlContents,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newUserMessage]);

    // 准备FormData
    const formData = new FormData();
    formData.append('message', userMessage);
    formData.append('session_id', sessionId || '');
    formData.append('user_id', currentUserId);
    formData.append('deep_thinking', deepThinking ? 'true' : 'false');
    if (urlContents.length > 0) {
      formData.append('url_contents', JSON.stringify(urlContents));
    }
    attachments.forEach((attachment) => {
      formData.append('files', attachment.file, attachment.name);
    });

    // 预插入空的 AI 消息占位
    const botMsgId = Date.now() + 1;
    setMessages(prev => [...prev, {
      id: botMsgId,
      role: 'assistant',
      content: '',
      streaming: true,
      timestamp: new Date()
    }]);

    // 使用流式 API
    abortRef.current = ChatAPI.sendMessageStreaming(formData, {
      onToken: (token) => {
        setMessages(prev => prev.map(msg =>
          msg.id === botMsgId
            ? { ...msg, content: msg.content + token }
            : msg
        ));
      },
      onDone: (data) => {
        setSessionId(data.session_id);
        setSuggestions(data.suggestions || []);
        setMessages(prev => prev.map(msg =>
          msg.id === botMsgId
            ? { ...msg, streaming: false, emotion: data.emotion }
            : msg
        ));
        setAttachments([]);
        setDetectedURLs([]);
        setIsLoading(false);
        abortRef.current = null;
      },
      onError: (errMsg) => {
        console.error('流式消息失败:', errMsg);
        setMessages(prev => prev.map(msg =>
          msg.id === botMsgId
            ? { ...msg, content: msg.content || `抱歉，我现在无法回应。${errMsg}`, streaming: false }
            : msg
        ));
        setIsLoading(false);
        abortRef.current = null;
      }
    });

  }, [isLoading, sessionId, currentUserId]);

  return {
    messages,
    setMessages,
    isLoading,
    sessionId,
    setSessionId,
    suggestions,
    setSuggestions,
    messagesEndRef,
    scrollToBottom,
    sendMessage
  };
};

