import styled from 'styled-components';
import { motion } from 'framer-motion';
import { emotionColors } from '../constants/emotions';
import { spin, pulse } from './animations';

export const Header = styled.div`
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  padding: 20px;
  text-align: center;
  position: relative;
`;

export const Title = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
`;

export const Subtitle = styled.p`
  font-size: 0.9rem;
  opacity: 0.9;
`;

export const MessageBubble = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

export const Avatar = styled.div`
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

export const MessageWrapper = styled.div`
  display: flex;
  flex-direction: column;
  max-width: 70%;
  
  @media (max-width: 768px) {
    max-width: 85%;
  }
`;

export const MessageContent = styled.div`
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

export const FeedbackButtons = styled.div`
  display: flex;
  gap: 6px;
  margin-top: 6px;
  opacity: 0.6;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 1;
  }
`;

export const FeedbackButton = styled(motion.button)`
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

export const EmotionTag = styled.span`
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

export const MessageTimestamp = styled.div`
  font-size: 0.7rem;
  color: ${props => props.isUser ? 'rgba(255, 255, 255, 0.7)' : '#999'};
  margin-top: 4px;
  text-align: ${props => props.isUser ? 'right' : 'left'};
`;

export const Suggestions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
`;

export const SuggestionChip = styled(motion.button)`
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

export const WelcomeMessage = styled(motion.div)`
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

export const LoadingIndicator = styled(motion.div)`
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
    animation: spin 1s linear infinite;
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
`;

