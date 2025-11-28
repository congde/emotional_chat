import styled from 'styled-components';
import { motion } from 'framer-motion';
import { emotionColors } from '../constants/emotions';

// 顶部对话标题栏
export const ChatHeader = styled.div`
  padding: 16px 60px;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
  transition: background 0.3s ease, border-color 0.3s ease;
  
  body[data-theme='dark'] & {
    background: #1a1a2e;
    border-bottom-color: #2a2a3e;
  }
  
  @media (max-width: 768px) {
    padding: 12px 16px;
  }
`;

export const ChatTitle = styled.h2`
  font-size: 16px;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0 0 4px 0;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #e0e0e0;
  }
`;

export const ChatSubtitle = styled.p`
  font-size: 12px;
  color: #bbb;
  margin: 0;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #666;
  }
`;

// 隐藏旧的 Header 组件
export const Header = styled.div`
  display: none;
`;

export const Title = styled.h1`
  display: none;
`;

export const Subtitle = styled.p`
  display: none;
`;

export const MessageBubble = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

export const Avatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.isUser ? '#6366f1' : '#f5f5f5'};
  color: ${props => props.isUser ? 'white' : '#666'};
  flex-shrink: 0;
  font-size: 14px;
  transition: background 0.3s ease, color 0.3s ease;

  body[data-theme='dark'] & {
    background: ${props => props.isUser ? '#6366f1' : '#2a2a3e'};
    color: ${props => props.isUser ? 'white' : '#b0b0b0'};
  }
`;

export const MessageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  max-width: calc(100% - 50px);
`;

export const MessageContent = styled.div`
  padding: 12px 16px;
  border-radius: ${props => props.isUser ? '16px 16px 4px 16px' : '16px 16px 16px 4px'};
  background: ${props => props.isUser ? '#f5f5f5' : 'transparent'};
  color: #1a1a1a;
  line-height: 1.7;
  word-wrap: break-word;
  font-size: 15px;
  transition: background 0.3s ease, color 0.3s ease;
  
  ${props => props.isUser && `
    background: #f5f5f5;
  `}
  
  body[data-theme='dark'] & {
    color: #e0e0e0;
    
    ${props => props.isUser && `
      background: #2a2a4e;
    `}
  }
  
  ${props => !props.isUser && props.emotion && props.emotion !== 'neutral' && `
    border-left: 3px solid ${emotionColors[props.emotion] || emotionColors.neutral};
    padding-left: 16px;
  `}
`;

// 思考状态指示器
export const ThinkingStatus = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
  margin-bottom: 12px;
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;
  
  svg {
    color: #6366f1;
  }

  body[data-theme='dark'] & {
    background: #2a2a3e;
    border-color: #3a3a4e;
    color: #b0b0b0;
  }
`;

export const FeedbackButtons = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 8px;
  opacity: 0;
  transition: opacity 0.2s;
  
  ${MessageBubble}:hover & {
    opacity: 1;
  }
`;

export const FeedbackButton = styled(motion.button)`
  background: transparent;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #888;
  transition: all 0.15s;
  
  &:hover {
    background: #f5f5f5;
    border-color: #ddd;
    color: #666;
  }

  body[data-theme='dark'] & {
    border-color: #3a3a4e;
    color: #999;
    
    &:hover {
      background: #2a2a3e;
      border-color: #4a4a5e;
      color: #b0b0b0;
    }
  }
`;

export const EmotionTag = styled.span`
  display: inline-block;
  background: ${props => emotionColors[props.emotion] || emotionColors.neutral};
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  margin-left: 8px;
  font-weight: 500;
`;

export const MessageTimestamp = styled.div`
  font-size: 11px;
  color: #bbb;
  margin-top: 6px;
  text-align: ${props => props.isUser ? 'right' : 'left'};
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #666;
  }
`;

export const Suggestions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
`;

export const SuggestionChip = styled(motion.button)`
  background: #fff;
  border: 1px solid #e5e5e5;
  color: #666;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s ease;
  
  &:hover {
    background: #f5f5f5;
    border-color: #6366f1;
    color: #6366f1;
  }

  body[data-theme='dark'] & {
    background: #2a2a3e;
    border-color: #3a3a4e;
    color: #b0b0b0;
    
    &:hover {
      background: #3a3a4e;
      border-color: #6366f1;
      color: #6366f1;
    }
  }
`;

export const WelcomeMessage = styled(motion.div)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  text-align: center;
  padding: 60px 20px;
  
  h3 {
    font-size: 28px;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 16px;
    transition: color 0.3s ease;
  }
  
  p {
    font-size: 14px;
    color: #999;
    line-height: 1.8;
    max-width: 360px;
    transition: color 0.3s ease;
  }

  body[data-theme='dark'] & {
    h3 {
      color: #e0e0e0;
    }
    
    p {
      color: #888;
    }
  }
`;

export const LoadingIndicator = styled(motion.div)`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 13px;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  max-width: 900px;
  margin: 0 auto;
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;

  body[data-theme='dark'] & {
    background: #2a2a3e;
    border-color: #3a3a4e;
    color: #b0b0b0;
  }
  
  .spinner {
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
  
  .dots span {
    animation: pulse 1.4s ease-in-out infinite;
    margin: 0 1px;
  }
  
  .dots span:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .dots span:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes pulse {
    0%, 80%, 100% { opacity: 0.3; }
    40% { opacity: 1; }
  }
`;

