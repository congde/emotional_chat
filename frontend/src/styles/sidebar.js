import styled from 'styled-components';
import { motion } from 'framer-motion';

export const SidebarHeader = styled.div`
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid #f0f0f0;
  transition: border-color 0.3s ease;

  body[data-theme='dark'] & {
    border-bottom-color: #2a2a3e;
  }
`;

export const UserAvatar = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
`;

export const UserName = styled.div`
  font-weight: 600;
  color: #1a1a1a;
  font-size: 16px;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #e0e0e0;
  }
`;

export const NewChatButton = styled(motion.button)`
  margin: 16px;
  background: #f0f0ff;
  color: #6366f1;
  border: none;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e0e0ff;
  }
`;

export const SettingsButton = styled(motion.button)`
  margin: 0 16px 8px;
  background: transparent;
  border: none;
  color: #666;
  padding: 10px 12px;
  border-radius: 8px;
  font-weight: 400;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f5f5f5;
    color: #333;
  }

  body[data-theme='dark'] & {
    color: #b0b0b0;
    
    &:hover {
      background: #2a2a3e;
      color: #e0e0e0;
    }
  }
`;

export const HistorySection = styled.div`
  flex: 1;
  padding: 0 8px;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 4px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #ddd;
    border-radius: 4px;
  }
`;

export const HistoryTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #999;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 12px 12px 8px;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #666;
  }
`;

export const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

export const HistoryItem = styled(motion.div)`
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: ${props => props.active ? '#f0f0ff' : 'transparent'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  
  &:hover {
    background: ${props => props.active ? '#f0f0ff' : '#f5f5f5'};
  }

  body[data-theme='dark'] & {
    background: ${props => props.active ? '#2a2a4e' : 'transparent'};
    
    &:hover {
      background: ${props => props.active ? '#2a2a4e' : '#2a2a3e'};
    }
  }
`;

export const HistoryItemContent = styled.div`
  flex: 1;
  min-width: 0;
`;

export const HistoryItemActions = styled.div`
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.15s ease;
  
  ${HistoryItem}:hover & {
    opacity: 1;
  }
`;

export const DeleteButton = styled(motion.button)`
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  
  &:hover {
    background: #fee;
    color: #f56565;
  }
`;

export const HistoryItemTitle = styled.div`
  font-size: 14px;
  color: #333;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #e0e0e0;
  }
`;

export const HistoryItemTime = styled.div`
  font-size: 12px;
  color: #999;
`;

export const HistoryItemPreview = styled.div`
  font-size: 12px;
  color: #999;
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

export const HistoryItemMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: 11px;
  color: #bbb;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #666;
  }
`;

export const MessageCountBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 1px 6px;
  background: #f0f0ff;
  color: #6366f1;
  border-radius: 10px;
  font-weight: 500;
  font-size: 11px;
`;

export const EmptyHistoryState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #bbb;
  text-align: center;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #666;
  }
`;

export const EmptyHistoryIcon = styled.div`
  font-size: 2.5rem;
  margin-bottom: 12px;
  opacity: 0.5;
`;

export const EmptyHistoryText = styled.div`
  font-size: 13px;
  line-height: 1.5;
`;

