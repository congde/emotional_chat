import styled from 'styled-components';
import { motion } from 'framer-motion';

export const SidebarHeader = styled.div`
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
`;

export const UserAvatar = styled.div`
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

export const UserName = styled.div`
  font-weight: 600;
  color: #333;
  font-size: 1.1rem;
`;

export const SettingsButton = styled(motion.button)`
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

export const NewChatButton = styled(motion.button)`
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

export const HistorySection = styled.div`
  flex: 1;
  padding: 0 20px;
  overflow-y: auto;
`;

export const HistoryTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
  font-size: 0.9rem;
  width: 100%;
`;

export const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

export const HistoryItem = styled(motion.div)`
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

export const HistoryItemContent = styled.div`
  flex: 1;
  min-width: 0;
`;

export const HistoryItemActions = styled.div`
  display: flex;
  align-items: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  
  ${HistoryItem}:hover & {
    opacity: 1;
  }
`;

export const DeleteButton = styled(motion.button)`
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

export const HistoryItemTitle = styled.div`
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 4px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

export const HistoryItemTime = styled.div`
  font-size: 0.75rem;
  color: #666;
  margin-top: 4px;
`;

export const HistoryItemPreview = styled.div`
  font-size: 0.8rem;
  color: #999;
  margin-top: 4px;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
`;

export const HistoryItemMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 0.7rem;
  color: #999;
`;

export const MessageCountBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  border-radius: 10px;
  font-weight: 500;
`;

export const EmptyHistoryState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #999;
  text-align: center;
`;

export const EmptyHistoryIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 16px;
  opacity: 0.5;
`;

export const EmptyHistoryText = styled.div`
  font-size: 0.9rem;
  line-height: 1.6;
`;

