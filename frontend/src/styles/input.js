import styled from 'styled-components';
import { motion } from 'framer-motion';

export const InputWrapper = styled.div`
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
`;

export const InputBox = styled.div`
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 16px;
  padding: 12px 16px;
  transition: all 0.2s ease;
  
  &:focus-within {
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  }

  body[data-theme='dark'] & {
    background: #2a2a3e;
    border-color: #3a3a4e;
    
    &:focus-within {
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
  }
`;

export const MessageInput = styled.textarea`
  width: 100%;
  border: none;
  font-size: 15px;
  outline: none;
  resize: none;
  min-height: 24px;
  max-height: 200px;
  line-height: 1.5;
  color: #1a1a1a;
  background: transparent;
  transition: color 0.3s ease;
  
  &::placeholder {
    color: #bbb;
    transition: color 0.3s ease;
  }

  body[data-theme='dark'] & {
    color: #e0e0e0;
    
    &::placeholder {
      color: #666;
    }
  }
`;

export const InputActions = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  transition: border-color 0.3s ease;

  body[data-theme='dark'] & {
    border-top-color: #2a2a3e;
  }
`;

export const LeftActions = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

export const RightActions = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

export const ActionButton = styled(motion.button)`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  
  &:hover {
    background: #f5f5f5;
    color: #666;
  }
  
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  body[data-theme='dark'] & {
    color: #999;
    
    &:hover {
      background: #2a2a3e;
      color: #b0b0b0;
    }
  }
`;

export const FeatureButton = styled(motion.button)`
  padding: 6px 12px;
  border-radius: 16px;
  background: ${props => props.active ? '#f0f0ff' : 'transparent'};
  border: 1px solid ${props => props.active ? '#6366f1' : '#e5e5e5'};
  color: ${props => props.active ? '#6366f1' : '#666'};
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
  
  &:hover {
    background: #f5f5f5;
    border-color: #ddd;
  }

  body[data-theme='dark'] & {
    background: ${props => props.active ? '#2a2a4e' : 'transparent'};
    border-color: ${props => props.active ? '#6366f1' : '#3a3a4e'};
    color: ${props => props.active ? '#6366f1' : '#b0b0b0'};
    
    &:hover {
      background: #2a2a3e;
      border-color: #4a4a5e;
    }
  }
`;

export const AttachmentButton = styled(motion.button)`
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: transparent;
  border: none;
  color: #888;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  
  &:hover {
    background: #f5f5f5;
    color: #666;
  }
  
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
`;

export const SendButton = styled(motion.button)`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: ${props => props.disabled ? '#e5e5e5' : '#6366f1'};
  border: none;
  color: white;
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  
  &:hover:not(:disabled) {
    background: #5558e3;
  }
`;

export const FileInput = styled.input`
  display: none;
`;

export const AttachmentsPreview = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
`;

export const AttachmentItem = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 13px;
  color: #666;
  transition: background 0.3s ease, color 0.3s ease;

  body[data-theme='dark'] & {
    background: #2a2a3e;
    color: #b0b0b0;
  }
`;

export const AttachmentIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6366f1;
`;

export const RemoveAttachmentButton = styled.button`
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: #eee;
    color: #666;
  }
`;

export const URLPreview = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  font-size: 13px;
  color: #16a34a;
  margin-bottom: 12px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
`;

export const URLText = styled.span`
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

export const URLButton = styled.button`
  background: none;
  border: none;
  color: #16a34a;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(22, 163, 74, 0.1);
  }
`;

// 快捷功能按钮区域
export const QuickActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
`;

export const QuickActionButton = styled(motion.button)`
  padding: 8px 16px;
  border-radius: 20px;
  background: #fff;
  border: 1px solid #e5e5e5;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
  
  &:hover {
    background: #f5f5f5;
    border-color: #6366f1;
    color: #6366f1;
  }
  
  svg {
    width: 16px;
    height: 16px;
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

