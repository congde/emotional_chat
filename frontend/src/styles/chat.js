import styled from 'styled-components';
import { motion } from 'framer-motion';
import { emotionColors } from '../constants/emotions';

// 顶部对话标题栏
export const ChatHeader = styled.div`
  min-height: 58px;
  padding: 10px 22px;
  border-bottom: 1px solid var(--border-default);
  background: var(--bg-panel);
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: background 0.3s ease, border-color 0.3s ease;
  
  body[data-theme='dark'] & {
    background: rgba(20, 20, 34, 0.8);
    border-bottom-color: rgba(255, 255, 255, 0.04);
  }
  
  @media (max-width: 768px) {
    padding: 12px 16px;
  }
`;

export const ChatTitle = styled.h2`
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
  letter-spacing: -0.3px;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #f1f5f9;
  }
`;

export const ChatSubtitle = styled.p`
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #475569;
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
  gap: 14px;
  max-width: 760px;
  margin: 0 auto;
  width: 100%;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

export const Avatar = styled.div`
  width: 30px;
  height: 30px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.isUser
    ? '#202327'
    : 'var(--bg-subtle)'
  };
  color: ${props => props.isUser ? 'white' : 'var(--text-secondary)'};
  flex-shrink: 0;
  font-size: 15px;
  transition: background 0.3s ease, color 0.3s ease;
  box-shadow: none;

  body[data-theme='dark'] & {
    background: ${props => props.isUser
      ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)'
      : 'linear-gradient(135deg, #1e293b 0%, #334155 100%)'
    };
    color: ${props => props.isUser ? 'white' : '#94a3b8'};
  }
`;

export const MessageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  max-width: calc(100% - 54px);
`;

export const MessageContent = styled.div`
  padding: ${props => props.isUser ? '11px 14px' : '2px 0'};
  border-radius: 14px;
  background: ${props => props.isUser
    ? 'var(--bg-subtle)'
    : 'transparent'
  };
  color: var(--text-primary);
  line-height: 1.7;
  word-wrap: break-word;
  font-size: 14.5px;
  transition: background 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: none;
  
  body[data-theme='dark'] & {
    color: ${props => props.isUser ? '#ffffff' : '#e2e8f0'};
    background: ${props => props.isUser
      ? 'linear-gradient(135deg, #6366f1 0%, #818cf8 100%)'
      : '#1e293b'
    };
    box-shadow: ${props => props.isUser
      ? '0 2px 12px rgba(99, 102, 241, 0.3)'
      : '0 1px 4px rgba(0, 0, 0, 0.2)'
    };
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
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 12px;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 12px;
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;
  
  svg {
    color: #6366f1;
  }

  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.06);
    color: #94a3b8;
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
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: #94a3b8;
  transition: all 0.15s;
  
  &:hover {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.2);
    color: #6366f1;
  }

  body[data-theme='dark'] & {
    border-color: rgba(255, 255, 255, 0.08);
    color: #64748b;
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
      border-color: rgba(99, 102, 241, 0.3);
      color: #818cf8;
    }
  }
`;

export const EmotionTag = styled.span`
  display: inline-block;
  background: ${props => emotionColors[props.emotion] || emotionColors.neutral};
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 11px;
  margin-left: 8px;
  font-weight: 600;
  letter-spacing: 0.3px;
`;

export const MessageTimestamp = styled.div`
  font-size: 11px;
  color: #cbd5e1;
  margin-top: 6px;
  text-align: ${props => props.isUser ? 'right' : 'left'};
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #475569;
  }
`;

export const Suggestions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
  max-width: 820px;
  margin-left: auto;
  margin-right: auto;
`;

export const SuggestionChip = styled(motion.button)`
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: #475569;
  padding: 8px 16px;
  border-radius: 24px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  
  &:hover {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.3);
    color: #6366f1;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.1);
    transform: translateY(-1px);
  }

  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.06);
    color: #94a3b8;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
      border-color: rgba(99, 102, 241, 0.3);
      color: #818cf8;
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
    font-size: 32px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
    transition: color 0.3s ease;
  }
  
  p {
    font-size: 15px;
    color: #94a3b8;
    line-height: 1.8;
    max-width: 420px;
    transition: color 0.3s ease;
  }

  body[data-theme='dark'] & {
    h3 {
      color: #f1f5f9;
    }
    
    p {
      color: #64748b;
    }
  }
`;

export const LoadingIndicator = styled(motion.div)`
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 13px;
  padding: 10px 18px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 14px;
  max-width: 820px;
  margin: 0 auto;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  transition: background 0.3s ease, border-color 0.3s ease, color 0.3s ease;

  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.06);
    color: #94a3b8;
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

