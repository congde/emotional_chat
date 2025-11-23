import styled from 'styled-components';
import { motion } from 'framer-motion';

export const MessageInput = styled.input`
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

export const AttachmentButton = styled(motion.button)`
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

export const SendButton = styled(motion.button)`
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

export const FileInput = styled.input`
  display: none;
`;

export const AttachmentsPreview = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
`;

export const AttachmentItem = styled(motion.div)`
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

export const AttachmentIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const RemoveAttachmentButton = styled.button`
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

export const URLPreview = styled(motion.div)`
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

export const URLText = styled.span`
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

export const URLButton = styled.button`
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

