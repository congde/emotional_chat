import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Heart, User, Bot, Loader2, Plus, Clock, Paperclip, X, FileText, Image, Link, ExternalLink, MessageSquarePlus, Trash2, Settings } from 'lucide-react';
import ChatAPI from './services/ChatAPI';
import TypewriterComponent from './components/TypewriterText';
import PersonalizationPanel from './components/PersonalizationPanel';

// 旋转动画
const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

// 脉动动画
const pulse = keyframes`
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
`;

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const Sidebar = styled(motion.div)`
  width: 300px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    width: 100%;
    max-height: 40vh;
    border-right: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }
`;

const SidebarHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
`;

const UserAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
`;

const UserName = styled.div`
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
`;

const SettingsButton = styled(motion.button)`
  width: 100%;
  background: transparent;
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 20px;
  margin-top: 10px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    transform: translateY(-1px);
  }
`;

const NewChatButton = styled(motion.button)`
  width: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 20px;
  margin-top: 0;
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
`;


const HistorySection = styled.div`
  flex: 1;
  padding: 0 20px;
  overflow-y: auto;
`;

const HistoryTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
  font-size: 0.9rem;
`;

const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const HistoryItem = styled(motion.div)`
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: ${props => props.active ? 'rgba(102, 126, 234, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.active ? 'rgba(102, 126, 234, 0.3)' : 'transparent'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  
  &:hover {
    background: rgba(102, 126, 234, 0.05);
  }
`;

const HistoryItemContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const HistoryItemActions = styled.div`
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  
  ${HistoryItem}:hover & {
    opacity: 1;
  }
`;

const DeleteButton = styled(motion.button)`
  background: none;
  border: none;
  color: #ff6b6b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(255, 107, 107, 0.1);
    transform: scale(1.1);
  }
`;

const HistoryItemTitle = styled.div`
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const HistoryItemTime = styled.div`
  font-size: 0.75rem;
  color: #666;
`;

const ChatContainer = styled(motion.div)`
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(10px);
`;

const Header = styled.div`
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  padding: 20px;
  text-align: center;
  position: relative;
`;

const Title = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
`;

const Subtitle = styled.p`
  font-size: 0.9rem;
  opacity: 0.9;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const MessageBubble = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.isUser ? '#667eea' : '#ff6b6b'};
  color: white;
  flex-shrink: 0;
`;

const MessageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 70%;
  
  @media (max-width: 768px) {
    max-width: 85%;
  }
`;

const emotionColors = {
  happy: '#ffd93d',
  sad: '#74b9ff',
  angry: '#fd79a8',
  anxious: '#a29bfe',
  excited: '#fdcb6e',
  confused: '#6c5ce7',
  frustrated: '#e84393',
  lonely: '#636e72',
  grateful: '#00b894',
  neutral: '#b2bec3'
};

const emotionLabels = {
  happy: '开心',
  sad: '难过',
  angry: '愤怒',
  anxious: '焦虑',
  excited: '兴奋',
  confused: '困惑',
  frustrated: '沮丧',
  lonely: '孤独',
  grateful: '感恩',
  neutral: '平静'
};

const MessageContent = styled.div`
  padding: 12px 16px;
  border-radius: 18px;
  background: ${props => props.isUser ? '#667eea' : '#f8f9fa'};
  color: ${props => props.isUser ? 'white' : '#333'};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  line-height: 1.6;
  word-wrap: break-word;
  
  /* AI消息根据情绪添加左边框 */
  ${props => !props.isUser && props.emotion && props.emotion !== 'neutral' && `
    border-left: 4px solid ${emotionColors[props.emotion] || emotionColors.neutral};
    padding-left: 16px;
  `}
  
  &::before {
    content: '';
    position: absolute;
    top: 10px;
    ${props => props.isUser ? 'right: -8px;' : 'left: -8px;'}
    width: 0;
    height: 0;
    border: 8px solid transparent;
    border-${props => props.isUser ? 'left' : 'right'}-color: ${props => props.isUser ? '#667eea' : '#f8f9fa'};
  }
`;

const FeedbackButtons = styled.div`
  display: flex;
  gap: 6px;
  margin-top: 6px;
  opacity: 0.6;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 1;
  }
`;

const FeedbackButton = styled(motion.button)`
  background: transparent;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(102, 126, 234, 0.1);
    border-color: #667eea;
    color: #667eea;
  }
`;

const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
`;

const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  
  h3 {
    margin: 0;
    color: #333;
    font-size: 1.3rem;
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #333;
  }
`;

const FeedbackTypeButtons = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
`;

const TypeButton = styled(motion.button)`
  padding: 10px 16px;
  border-radius: 10px;
  border: 2px solid ${props => props.active ? '#667eea' : '#ddd'};
  background: ${props => props.active ? 'rgba(102, 126, 234, 0.1)' : 'white'};
  color: ${props => props.active ? '#667eea' : '#666'};
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  
  &:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
  }
`;

const RatingContainer = styled.div`
  margin-bottom: 20px;
  
  label {
    display: block;
    margin-bottom: 10px;
    color: #333;
    font-weight: 500;
  }
`;

const RatingStars = styled.div`
  display: flex;
  gap: 8px;
`;

const StarButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: 2rem;
  color: ${props => props.active ? '#ffd93d' : '#ddd'};
  transition: all 0.2s;
  padding: 0;
  
  &:hover {
    transform: scale(1.1);
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SubmitButton = styled(motion.button)`
  width: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 20px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const EmotionTag = styled.span`
  display: inline-block;
  background: ${props => emotionColors[props.emotion] || emotionColors.neutral};
  color: white;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-left: 8px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
  }
`;

const MessageTimestamp = styled.div`
  font-size: 0.7rem;
  color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.7)' : '#999'};
  margin-top: 4px;
  text-align: ${props => props.isUser ? 'right' : 'left'};
`;

const Suggestions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
`;

const SuggestionChip = styled(motion.button)`
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-1px);
  }
`;

const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const InputRow = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

const AttachmentButton = styled(motion.button)`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  
  @media (max-width: 768px) {
    width: 48px;
    height: 48px;
  }
`;

const FileInput = styled.input`
  display: none;
`;

const AttachmentsPreview = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
`;

const AttachmentItem = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  font-size: 0.9rem;
  color: #667eea;
`;

const AttachmentIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

const RemoveAttachmentButton = styled.button`
  background: none;
  border: none;
  color: #ff6b6b;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(255, 107, 107, 0.1);
  }
`;

const URLPreview = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(0, 184, 148, 0.1);
  border: 1px solid rgba(0, 184, 148, 0.3);
  border-radius: 20px;
  font-size: 0.9rem;
  color: #00b894;
  margin-bottom: 10px;
`;

const URLText = styled.span`
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const URLButton = styled.button`
  background: none;
  border: none;
  color: #00b894;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(0, 184, 148, 0.1);
  }
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s ease;
  
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SendButton = styled(motion.button)`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  
  &:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  
  @media (max-width: 768px) {
    width: 48px;
    height: 48px;
  }
`;

const LoadingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 10px;
  color: #666;
  font-size: 0.9rem;
  padding: 12px 18px;
  background: #f8f9fa;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  
  .spinner {
    animation: ${spin} 1s linear infinite;
  }
  
  .dots span {
    animation: ${pulse} 1.4s ease-in-out infinite;
    margin: 0 1px;
  }
  
  .dots span:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .dots span:nth-child(3) {
    animation-delay: 0.4s;
  }
`;

const WelcomeMessage = styled(motion.div)`
  text-align: center;
  color: #666;
  padding: 40px 20px;
  
  h3 {
    margin-bottom: 10px;
    color: #333;
  }
  
  p {
    line-height: 1.6;
  }
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [historySessions, setHistorySessions] = useState([]);
  const [showPersonalizationPanel, setShowPersonalizationPanel] = useState(false);
  
  // 从localStorage读取或生成用户ID
  const [currentUserId] = useState(() => {
    const savedUserId = localStorage.getItem('emotional_chat_user_id');
    if (savedUserId) {
      console.log('使用已保存的用户ID:', savedUserId);
      return savedUserId;
    }
    const newUserId = `user_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    console.log('生成新的用户ID:', newUserId);
    localStorage.setItem('emotional_chat_user_id', newUserId);
    return newUserId;
  });
  
  const [attachments, setAttachments] = useState([]);
  const [detectedURLs, setDetectedURLs] = useState([]);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState(null);
  const [feedbackType, setFeedbackType] = useState('');
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const inputRef = useRef(null);

  // 格式化时间戳
  const formatTimestamp = (date) => {
    if (!date) return '';
    const now = new Date();
    const messageDate = new Date(date);
    const diffMs = now - messageDate;
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}小时前`;
    
    return messageDate.toLocaleString('zh-CN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  // 会话ID改变时保存到localStorage
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('emotional_chat_current_session', sessionId);
    }
  }, [sessionId]);

  // 加载历史会话
  const loadHistorySessions = useCallback(async () => {
    try {
      console.log('正在加载历史会话，用户ID:', currentUserId);
      const response = await ChatAPI.getUserSessions(currentUserId);
      console.log('历史会话响应:', response);
      setHistorySessions(response.sessions || []);
    } catch (error) {
      console.error('加载历史会话失败:', error);
    }
  }, [currentUserId]);

  useEffect(() => {
    loadHistorySessions();
  }, [loadHistorySessions]);

  const deleteConversation = async (targetSessionId, event) => {
    event.stopPropagation(); // 阻止触发父级的点击事件
    
    if (window.confirm('确定要删除这个对话吗？此操作无法撤销。')) {
      try {
        await ChatAPI.deleteSession(targetSessionId);
        
        // 如果删除的是当前会话，清空消息
        if (targetSessionId === sessionId) {
          setMessages([]);
          setSessionId(null);
          loadedSessionIdRef.current = null; // 清除已加载会话记录
          setSuggestions([]);
        }
        
        // 刷新历史会话列表
        loadHistorySessions();
        
        console.log('对话删除成功');
      } catch (error) {
        console.error('删除对话失败:', error);
        alert('删除对话失败，请稍后重试');
      }
    }
  };

  const startNewChat = () => {
    setMessages([]);
    setSessionId(null);
    loadedSessionIdRef.current = null; // 清除已加载会话记录
    setSuggestions([]);
    setAttachments([]);
    setDetectedURLs([]);
  };

  // URL检测函数
  const detectURLs = (text) => {
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    return text.match(urlRegex) || [];
  };

  // 处理URL内容
  const processURL = async (url) => {
    try {
      const response = await ChatAPI.parseURL({ url });
      return response;
    } catch (error) {
      console.error('URL解析失败:', error);
      return null;
    }
  };

  // 处理文件上传
  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const newAttachments = files.map(file => ({
      id: Date.now() + Math.random(),
      file,
      name: file.name,
      size: file.size,
      type: file.type
    }));
    setAttachments(prev => [...prev, ...newAttachments]);
  };

  // 移除附件
  const removeAttachment = (attachmentId) => {
    setAttachments(prev => prev.filter(att => att.id !== attachmentId));
  };

  // 获取文件图标
  const getFileIcon = (fileType) => {
    if (fileType.startsWith('image/')) return <Image size={16} />;
    if (fileType === 'application/pdf') return <FileText size={16} />;
    return <FileText size={16} />;
  };

  // 格式化文件大小
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 使用 ref 来防止重复调用，避免 React StrictMode 导致的重复执行
  const isLoadingHistoryRef = useRef(false);
  const currentLoadingSessionIdRef = useRef(null);
  const loadedSessionIdRef = useRef(null); // 记录已加载的会话ID
  
  const loadSessionHistory = useCallback(async (targetSessionId) => {
    console.log('[loadSessionHistory] 开始加载会话:', targetSessionId);
    console.log('[loadSessionHistory] 当前状态 - isLoadingHistory:', isLoadingHistoryRef.current, 'currentSessionId:', currentLoadingSessionIdRef.current);
    console.log('[loadSessionHistory] 已加载会话:', loadedSessionIdRef.current);
    
    // 防止重复调用：如果正在加载相同的会话，直接返回
    if (isLoadingHistoryRef.current && currentLoadingSessionIdRef.current === targetSessionId) {
      console.warn('[loadSessionHistory] 正在加载该会话，跳过重复请求');
      return;
    }
    
    // 如果已经加载了相同的会话，不重复加载
    if (targetSessionId === loadedSessionIdRef.current) {
      console.log('[loadSessionHistory] 会话已加载，跳过重复加载');
      return;
    }
    
    // 设置加载状态
    isLoadingHistoryRef.current = true;
    currentLoadingSessionIdRef.current = targetSessionId;
    console.log('[loadSessionHistory] 设置加载状态为 true');
    
    try {
      console.log('[loadSessionHistory] 发送API请求...');
      const response = await ChatAPI.getSessionHistory(targetSessionId);
      console.log('[loadSessionHistory] 收到响应:', response);
      console.log('[loadSessionHistory] 响应类型:', typeof response);
      console.log('[loadSessionHistory] 消息数量:', response?.messages?.length || 0);
      
      // 检查响应格式
      if (!response || !response.messages) {
        console.error('[loadSessionHistory] 响应格式错误:', response);
        setMessages([]);
        return;
      }
      
      // 检查是否有重复消息
      const messageKeys = new Set();
      const duplicates = [];
      response.messages.forEach((msg, idx) => {
        const key = `${msg.role}_${msg.content}_${msg.timestamp}`;
        if (messageKeys.has(key)) {
          duplicates.push({ index: idx, key, message: msg });
        } else {
          messageKeys.add(key);
        }
      });
      
      if (duplicates.length > 0) {
        console.warn('[loadSessionHistory] 后端返回了重复消息:', duplicates);
      }
      
      // 后端返回的是按时间倒序，需要转换为正序
      // 先创建消息对象，然后去重和排序
      const messageMap = new Map(); // 用于去重，key是数据库ID
      const contentKeyMap = new Map(); // 记录内容+角色的组合，用于检测内容重复（忽略时间戳）
      
      response.messages.forEach((msg, index) => {
        // 使用数据库ID作为主要标识
        const dbId = msg.id;
        
        // 创建内容key（只基于角色和内容，忽略时间戳），用于检测内容重复
        const contentKey = `${msg.role}_${msg.content}`;
        
        // 如果消息有数据库ID，使用ID作为主要去重依据
        if (dbId) {
          // 首先检查数据库ID是否重复
          if (messageMap.has(dbId)) {
            console.warn('[loadSessionHistory] 发现重复的数据库ID，已跳过:', dbId);
            return; // 跳过重复的ID
          }
          
          // 然后检查内容是否重复（即使时间戳不同）
          if (contentKeyMap.has(contentKey)) {
            const existingMsg = contentKeyMap.get(contentKey);
            // 如果内容相同，保留时间更早的那条（通常是第一条）
            const currentTime = new Date(msg.timestamp);
            const existingTime = existingMsg.timestamp;
            if (currentTime >= existingTime) {
              console.warn('[loadSessionHistory] 发现重复的消息内容（时间较晚），已跳过:', contentKey, '保留ID:', existingMsg.dbId);
              return; // 跳过内容重复且时间较晚的消息
            } else {
              // 如果当前消息时间更早，移除之前的，保留当前的
              console.warn('[loadSessionHistory] 发现重复的消息内容（时间较早），替换之前的:', contentKey);
              messageMap.delete(existingMsg.dbId);
            }
          }
          
          const messageObj = {
            id: `history_${targetSessionId}_${dbId}_${msg.timestamp}`,
            role: msg.role,
            content: msg.content,
            emotion: msg.emotion,
            timestamp: new Date(msg.timestamp),
            dbId: dbId, // 保存数据库ID用于排序
            isHistory: true // 标记为历史消息
          };
          
          messageMap.set(dbId, messageObj);
          contentKeyMap.set(contentKey, messageObj);
        } else {
          // 如果没有数据库ID，使用内容+时间作为key
          if (contentKeyMap.has(contentKey)) {
            console.warn('[loadSessionHistory] 发现重复的消息内容（无ID），已跳过:', contentKey);
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
      
      // 转换为数组
      const sessionMessages = Array.from(messageMap.values());
      
      // 确保消息按时间正序排列（如果时间相同，按数据库ID排序）
      sessionMessages.sort((a, b) => {
        const timeDiff = a.timestamp - b.timestamp;
        if (timeDiff !== 0) return timeDiff;
        // 如果时间相同，按数据库ID排序
        if (a.dbId !== undefined && b.dbId !== undefined) {
          return a.dbId - b.dbId;
        }
        // 如果时间相同且没有ID，user消息应该在assistant之前
        if (a.role === 'user' && b.role === 'assistant') return -1;
        if (a.role === 'assistant' && b.role === 'user') return 1;
        return 0;
      });
      
      console.log('[loadSessionHistory] 去重并排序后的消息数量:', sessionMessages.length);
      console.log('[loadSessionHistory] 消息列表:', sessionMessages.map(m => ({ 
        id: m.id, 
        role: m.role, 
        content: m.content.substring(0, 30), 
        timestamp: m.timestamp.toISOString() 
      })));
      
      console.log('[loadSessionHistory] 准备设置消息，最终消息数量:', sessionMessages.length);
      
      // 如果没有消息，也要设置空数组，这样前端可以显示空状态
      if (sessionMessages.length === 0) {
        console.warn('[loadSessionHistory] 会话没有消息，设置空数组');
        setMessages([]);
        setSessionId(targetSessionId);
        loadedSessionIdRef.current = targetSessionId;
        setSuggestions([]);
        return;
      }
      
      // 使用函数式更新，确保不会重复设置
      console.log('[loadSessionHistory] 准备设置消息到state，消息数量:', sessionMessages.length);
      console.log('[loadSessionHistory] 消息详情:', sessionMessages.map(m => ({
        id: m.id,
        role: m.role,
        contentLength: m.content.length,
        timestamp: m.timestamp.toISOString()
      })));
      
      setMessages(sessionMessages);
      setSessionId(targetSessionId);
      loadedSessionIdRef.current = targetSessionId; // 记录已加载的会话
      setSuggestions([]);
      
      // 注意：这里不能直接访问messages，因为它是异步更新的
      // 消息会在下一次渲染时显示
      
      console.log('[loadSessionHistory] 消息已设置到state');
    } catch (error) {
      console.error('[loadSessionHistory] 加载会话历史失败:', error);
    } finally {
      isLoadingHistoryRef.current = false;
      currentLoadingSessionIdRef.current = null;
      console.log('[loadSessionHistory] 清除加载状态');
    }
  }, []); // 移除所有依赖，使用ref来跟踪状态

  const sendMessage = async () => {
    if ((!inputValue.trim() && attachments.length === 0) || isLoading) return;

    const userMessage = inputValue.trim();
    const urls = detectURLs(userMessage);
    
    // 处理检测到的URL
    let urlContents = [];
    if (urls.length > 0) {
      for (const url of urls) {
        const urlContent = await processURL(url);
        if (urlContent) {
          urlContents.push(urlContent);
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

    try {
      // 准备FormData用于文件上传
      const formData = new FormData();
      formData.append('message', userMessage);
      formData.append('session_id', sessionId || '');
      formData.append('user_id', currentUserId);
      
      // 添加URL内容
      if (urlContents.length > 0) {
        formData.append('url_contents', JSON.stringify(urlContents));
      }

      // 添加文件附件
      attachments.forEach((attachment, index) => {
        formData.append(`file_${index}`, attachment.file, attachment.name);
      });

      const response = await ChatAPI.sendMessageWithAttachments(formData);

      setSessionId(response.session_id);
      setSuggestions(response.suggestions || []);

      // 添加机器人回复
      const botMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        emotion: response.emotion,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

      // 清空附件和URL
      setAttachments([]);
      setDetectedURLs([]);

      // 刷新历史会话列表
      loadHistorySessions();

    } catch (error) {
      console.error('发送消息失败:', error);
      
      // 用户友好的错误提示
      let errorMsg = '抱歉，我现在无法回应。';
      if (error.response?.status === 500) {
        errorMsg += '服务器遇到了一些问题，请稍后再试。';
      } else if (error.message === 'Network Error') {
        errorMsg += '网络连接似乎有问题，请检查网络设置。';
      } else {
        errorMsg += '请稍后再试。';
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // 发送后重新聚焦输入框
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
    // 自动聚焦输入框，允许用户修改后发送
    inputRef.current?.focus();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // 防抖URL检测
  const debouncedDetectURLs = useCallback((text) => {
    const timeoutId = setTimeout(() => {
      const urls = detectURLs(text);
      setDetectedURLs(urls);
    }, 300);
    return () => clearTimeout(timeoutId);
  }, []);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setInputValue(value);
    
    // 防抖检测URL
    debouncedDetectURLs(value);
  };

  // 打开反馈模态框
  const openFeedbackModal = (message) => {
    setFeedbackMessage(message);
    setShowFeedbackModal(true);
    setFeedbackType('');
    setFeedbackRating(0);
    setFeedbackComment('');
  };

  // 关闭反馈模态框
  const closeFeedbackModal = () => {
    setShowFeedbackModal(false);
    setFeedbackMessage(null);
    setFeedbackType('');
    setFeedbackRating(0);
    setFeedbackComment('');
  };

  // 提交反馈
  const submitFeedback = async () => {
    if (!feedbackType || feedbackRating === 0) {
      alert('请选择反馈类型和评分');
      return;
    }

    try {
      // 找到用户消息（与bot回复对应的前一条消息）
      const messageIndex = messages.findIndex(m => m.id === feedbackMessage.id);
      const userMessage = messageIndex > 0 ? messages[messageIndex - 1] : null;

      const feedbackData = {
        session_id: sessionId || 'unknown',
        user_id: currentUserId,
        message_id: feedbackMessage.id,
        feedback_type: feedbackType,
        rating: feedbackRating,
        comment: feedbackComment,
        user_message: userMessage?.content || '',
        bot_response: feedbackMessage.content
      };

      await ChatAPI.submitFeedback(feedbackData);
      alert('感谢您的反馈！');
      closeFeedbackModal();
    } catch (error) {
      console.error('提交反馈失败:', error);
      alert('提交反馈失败，请稍后重试');
    }
  };

  return (
    <AppContainer>
      <Sidebar
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <SidebarHeader>
          <UserAvatar>
            <User size={20} />
          </UserAvatar>
          <UserName>情感伙伴</UserName>
        </SidebarHeader>

        <NewChatButton
          onClick={startNewChat}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Plus size={16} />
          新对话
        </NewChatButton>

        <SettingsButton
          onClick={() => setShowPersonalizationPanel(true)}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Settings size={16} />
          个性化配置
        </SettingsButton>
        

        <HistorySection>
          <HistoryTitle>
            <Clock size={16} />
            历史对话
          </HistoryTitle>
          <HistoryList>
            <AnimatePresence>
              {historySessions.map((session) => (
                <HistoryItem
                  key={session.session_id}
                  active={session.session_id === sessionId}
                  onClick={(e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    console.log('[onClick] 点击历史记录项:', session.session_id);
                    loadSessionHistory(session.session_id);
                  }}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <HistoryItemContent>
                    <HistoryItemTitle>{session.title}</HistoryItemTitle>
                    <HistoryItemTime>
                      {new Date(session.updated_at).toLocaleDateString()}
                    </HistoryItemTime>
                  </HistoryItemContent>
                  <HistoryItemActions>
                    <DeleteButton
                      onClick={(e) => deleteConversation(session.session_id, e)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      title="删除对话"
                    >
                      <Trash2 size={14} />
                    </DeleteButton>
                  </HistoryItemActions>
                </HistoryItem>
              ))}
            </AnimatePresence>
          </HistoryList>
        </HistorySection>
      </Sidebar>

      <ChatContainer
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Header>
          <Title>
            <Heart size={24} />
            情感聊天机器人
          </Title>
          <Subtitle>温暖陪伴，理解倾听</Subtitle>
        </Header>

        <MessagesContainer>
          <AnimatePresence initial={false}>
            {messages.length === 0 ? (
              <WelcomeMessage
                key="welcome"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ delay: 0.5 }}
              >
                <h3>👋 你好！我是你的情感支持伙伴</h3>
                <p>
                  我在这里倾听你的心声，理解你的感受。<br/>
                  无论是开心、难过、焦虑还是困惑，我都愿意陪伴你。<br/>
                  请随意分享你的想法和感受吧！
                </p>
              </WelcomeMessage>
            ) : (
              messages.map((message, index) => {
                console.log('[渲染消息]', index, message.id, message.role, message.content.substring(0, 20));
                return (
                <MessageBubble
                  key={message.id}
                  isUser={message.role === 'user'}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <Avatar isUser={message.role === 'user'}>
                    {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                  </Avatar>
                  <MessageWrapper>
                    <MessageContent 
                      isUser={message.role === 'user'}
                      emotion={message.emotion}
                    >
                      {message.role === 'assistant' && !message.isHistory ? (
                        <TypewriterComponent
                          text={message.content}
                          speed={message.emotion === 'sad' ? 40 : message.emotion === 'angry' ? 20 : message.emotion === 'happy' ? 25 : 30}
                          showCursor={true}
                          cursorColor={message.emotion === 'sad' ? '#74b9ff' : message.emotion === 'angry' ? '#ff7675' : message.emotion === 'happy' ? '#00b894' : '#333'}
                          isUser={false}
                        />
                      ) : (
                        message.content
                      )}
                      {message.emotion && message.emotion !== 'neutral' && (
                        <EmotionTag emotion={message.emotion}>
                          {emotionLabels[message.emotion] || message.emotion}
                        </EmotionTag>
                      )}
                    </MessageContent>
                    <MessageTimestamp isUser={message.role === 'user'}>
                      {formatTimestamp(message.timestamp)}
                    </MessageTimestamp>
                    {message.role === 'assistant' && (
                      <FeedbackButtons>
                        <FeedbackButton
                          onClick={() => openFeedbackModal(message)}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <MessageSquarePlus size={14} />
                          反馈
                        </FeedbackButton>
                      </FeedbackButtons>
                    )}
                  </MessageWrapper>
                </MessageBubble>
                );
              })
            )}
          </AnimatePresence>

          {isLoading && (
            <LoadingIndicator
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <Loader2 size={18} className="spinner" />
              <span>正在思考中</span>
              <span className="dots">
                <span>.</span>
                <span>.</span>
                <span>.</span>
              </span>
            </LoadingIndicator>
          )}

          {suggestions.length > 0 && (
            <Suggestions>
              <AnimatePresence>
                {suggestions.map((suggestion, index) => (
                  <SuggestionChip
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={() => handleSuggestionClick(suggestion)}
                  >
                    {suggestion}
                  </SuggestionChip>
                ))}
              </AnimatePresence>
            </Suggestions>
          )}

          <div ref={messagesEndRef} />
        </MessagesContainer>

        <InputContainer>
          {/* URL预览 */}
          {detectedURLs.length > 0 && (
            <URLPreview
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
            >
              <Link size={16} />
              <URLText>{detectedURLs[0]}</URLText>
              <URLButton onClick={() => window.open(detectedURLs[0], '_blank')}>
                <ExternalLink size={14} />
              </URLButton>
            </URLPreview>
          )}

          {/* 附件预览 */}
          {attachments.length > 0 && (
            <AttachmentsPreview>
              <AnimatePresence>
                {attachments.map((attachment) => (
                  <AttachmentItem
                    key={attachment.id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                  >
                    <AttachmentIcon>
                      {getFileIcon(attachment.type)}
                    </AttachmentIcon>
                    <span>{attachment.name}</span>
                    <span>({formatFileSize(attachment.size)})</span>
                    <RemoveAttachmentButton
                      onClick={() => removeAttachment(attachment.id)}
                    >
                      <X size={12} />
                    </RemoveAttachmentButton>
                  </AttachmentItem>
                ))}
              </AnimatePresence>
            </AttachmentsPreview>
          )}

          <InputRow>
            <MessageInput
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="分享你的想法和感受..."
              disabled={isLoading}
              aria-label="消息输入框"
              aria-describedby="input-hint"
            />
            <AttachmentButton
              onClick={() => fileInputRef.current?.click()}
              disabled={isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="添加附件"
              title="添加附件 (图片、PDF、文档)"
            >
              <Paperclip size={20} />
            </AttachmentButton>
            <SendButton
              onClick={sendMessage}
              disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="发送消息"
              aria-disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
              title="发送消息 (Enter)"
            >
              <Send size={20} />
            </SendButton>
          </InputRow>

          <FileInput
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,application/pdf,.doc,.docx,.txt"
            onChange={handleFileUpload}
          />
        </InputContainer>
      </ChatContainer>

      {/* 个性化配置面板 */}
      <PersonalizationPanel
        isOpen={showPersonalizationPanel}
        onClose={() => setShowPersonalizationPanel(false)}
        userId={currentUserId}
      />

      {/* 反馈模态框 */}
      <AnimatePresence>
        {showFeedbackModal && feedbackMessage && (
          <ModalOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeFeedbackModal}
          >
            <ModalContent
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
            >
              <ModalHeader>
                <h3>提交反馈</h3>
                <CloseButton onClick={closeFeedbackModal}>
                  <X size={20} />
                </CloseButton>
              </ModalHeader>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '500' }}>
                  反馈类型
                </label>
                <FeedbackTypeButtons>
                  <TypeButton
                    active={feedbackType === 'helpful'}
                    onClick={() => setFeedbackType('helpful')}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    ✅ 有帮助
                  </TypeButton>
                  <TypeButton
                    active={feedbackType === 'irrelevant'}
                    onClick={() => setFeedbackType('irrelevant')}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    ❌ 答非所问
                  </TypeButton>
                  <TypeButton
                    active={feedbackType === 'lack_empathy'}
                    onClick={() => setFeedbackType('lack_empathy')}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    😐 缺乏共情
                  </TypeButton>
                  <TypeButton
                    active={feedbackType === 'overstepping'}
                    onClick={() => setFeedbackType('overstepping')}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    ⚠️ 越界建议
                  </TypeButton>
                  <TypeButton
                    active={feedbackType === 'other'}
                    onClick={() => setFeedbackType('other')}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    📝 其他
                  </TypeButton>
                </FeedbackTypeButtons>
              </div>

              <RatingContainer>
                <label>评分</label>
                <RatingStars>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <StarButton
                      key={star}
                      active={feedbackRating >= star}
                      onClick={() => setFeedbackRating(star)}
                    >
                      {feedbackRating >= star ? '★' : '☆'}
                    </StarButton>
                  ))}
                </RatingStars>
              </RatingContainer>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '500' }}>
                  详细说明（选填）
                </label>
                <TextArea
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  placeholder="请描述您的具体感受或建议..."
                />
              </div>

              <SubmitButton
                onClick={submitFeedback}
                disabled={!feedbackType || feedbackRating === 0}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                提交反馈
              </SubmitButton>
            </ModalContent>
          </ModalOverlay>
        )}
      </AnimatePresence>
    </AppContainer>
  );
}

export default App;
