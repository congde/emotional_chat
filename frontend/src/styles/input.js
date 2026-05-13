import styled from 'styled-components';
import { motion } from 'framer-motion';

export const InputWrapper = styled.div`
  max-width: 820px;
  margin: 0 auto;
  width: 100%;
`;

export const InputBox = styled.div`
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 20px;
  padding: 14px 18px;
  transition: all 0.25s ease;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  
  &:focus-within {
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.08);
  }

  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
    
    &:focus-within {
      border-color: rgba(99, 102, 241, 0.5);
      box-shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
    }
  }
`;

export const MessageInput = styled.textarea`
  width: 100%;
  border: none;
  font-size: 15px;
  font-family: inherit;
  outline: none;
  resize: none;
  min-height: 24px;
  max-height: 200px;
  line-height: 1.5;
  color: #1a1a2e;
  background: transparent;
  transition: color 0.3s ease, height 0.1s ease;
  overflow-y: auto;
  
  &::placeholder {
    color: #cbd5e1;
    transition: color 0.3s ease;
  }

  body[data-theme='dark'] & {
    color: #f1f5f9;
    
    &::placeholder {
      color: #475569;
    }
  }
`;

export const InputActions = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(0, 0, 0, 0.04);
  transition: border-color 0.3s ease;

  body[data-theme='dark'] & {
    border-top-color: rgba(255, 255, 255, 0.04);
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
  border-radius: 10px;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  
  &:hover {
    background: rgba(99, 102, 241, 0.06);
    color: #6366f1;
  }
  
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  body[data-theme='dark'] & {
    color: #64748b;
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
      color: #818cf8;
    }
  }
`;

export const FeatureButton = styled(motion.button)`
  padding: 6px 14px;
  border-radius: 20px;
  background: ${props => props.$active ? 'rgba(99, 102, 241, 0.1)' : 'transparent'};
  border: 1px solid ${props => props.$active ? 'rgba(99, 102, 241, 0.3)' : 'rgba(0, 0, 0, 0.08)'};
  color: ${props => props.$active ? '#6366f1' : '#94a3b8'};
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.2);
    color: #6366f1;
  }

  body[data-theme='dark'] & {
    background: ${props => props.$active ? 'rgba(99, 102, 241, 0.15)' : 'transparent'};
    border-color: ${props => props.$active ? 'rgba(99, 102, 241, 0.3)' : 'rgba(255, 255, 255, 0.08)'};
    color: ${props => props.$active ? '#818cf8' : '#64748b'};
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
      border-color: rgba(99, 102, 241, 0.3);
      color: #818cf8;
    }
  }
`;

export const AttachmentButton = styled(motion.button)`
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  
  &:hover {
    background: rgba(99, 102, 241, 0.06);
    color: #6366f1;
  }
  
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  body[data-theme='dark'] & {
    color: #64748b;
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
      color: #818cf8;
    }
  }
`;

export const SendButton = styled(motion.button)`
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: ${props => props.disabled
    ? 'rgba(0, 0, 0, 0.06)'
    : 'linear-gradient(135deg, #6366f1 0%, #818cf8 100%)'
  };
  border: none;
  color: ${props => props.disabled ? '#cbd5e1' : '#ffffff'};
  cursor: ${props => props.disabled ? 'not-allowed' : 'pointer'};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: ${props => props.disabled ? 'none' : '0 2px 8px rgba(99, 102, 241, 0.3)'};
  
  &:hover:not(:disabled) {
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.4);
    transform: translateY(-1px);
  }

  body[data-theme='dark'] & {
    background: ${props => props.disabled
      ? 'rgba(255, 255, 255, 0.06)'
      : 'linear-gradient(135deg, #6366f1 0%, #818cf8 100%)'
    };
    color: ${props => props.disabled ? '#475569' : '#ffffff'};
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
  max-width: 820px;
  margin-left: auto;
  margin-right: auto;
`;

export const AttachmentItem = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.1);
  border-radius: 12px;
  font-size: 13px;
  color: #475569;
  transition: background 0.3s ease, color 0.3s ease;

  body[data-theme='dark'] & {
    background: rgba(99, 102, 241, 0.1);
    border-color: rgba(99, 102, 241, 0.15);
    color: #94a3b8;
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
  color: #94a3b8;
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(239, 68, 68, 0.08);
    color: #ef4444;
  }
`;

export const URLPreview = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.15);
  border-radius: 12px;
  font-size: 13px;
  color: #059669;
  margin-bottom: 12px;
  max-width: 820px;
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
  color: #059669;
  cursor: pointer;
  padding: 2px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background: rgba(16, 185, 129, 0.1);
  }
`;

// 快捷功能按钮区域
export const QuickActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
  max-width: 820px;
  margin-left: auto;
  margin-right: auto;
`;

export const QuickActionButton = styled(motion.button)`
  padding: 8px 16px;
  border-radius: 24px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  color: #64748b;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  
  &:hover {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.2);
    color: #6366f1;
    transform: translateY(-1px);
  }
  
  svg {
    width: 16px;
    height: 16px;
  }

  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.06);
    color: #94a3b8;
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
      border-color: rgba(99, 102, 241, 0.3);
      color: #818cf8;
    }
  }
`;

