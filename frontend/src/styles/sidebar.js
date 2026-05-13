import styled from 'styled-components';
import { motion } from 'framer-motion';

export const SidebarHeader = styled.div`
  padding: 20px 20px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  transition: border-color 0.3s ease;

  body[data-theme='dark'] & {
    border-bottom-color: rgba(255, 255, 255, 0.06);
  }
`;

export const UserAvatar = styled.div`
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
`;

export const UserName = styled.div`
  font-weight: 700;
  color: #1a1a2e;
  font-size: 17px;
  letter-spacing: -0.3px;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #f1f5f9;
  }
`;

export const NewChatButton = styled(motion.button)`
  margin: 16px 16px 8px;
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  color: #ffffff;
  border: none;
  padding: 11px 16px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  
  &:hover {
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
    transform: translateY(-1px);
  }
`;

export const SettingsButton = styled(motion.button)`
  margin: 0 16px 4px;
  background: transparent;
  border: none;
  color: #64748b;
  padding: 10px 12px;
  border-radius: 10px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(99, 102, 241, 0.06);
    color: #6366f1;
  }

  body[data-theme='dark'] & {
    color: #94a3b8;
    
    &:hover {
      background: rgba(99, 102, 241, 0.1);
      color: #818cf8;
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
    background: rgba(0, 0, 0, 0.08);
    border-radius: 4px;
  }
`;

export const HistoryTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #94a3b8;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  padding: 16px 12px 8px;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #475569;
  }
`;

export const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

export const HistoryItem = styled(motion.div)`
  padding: 10px 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: ${props => props.$active ? 'rgba(99, 102, 241, 0.08)' : 'transparent'};
  border-left: 3px solid ${props => props.$active ? '#6366f1' : 'transparent'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  
  &:hover {
    background: ${props => props.$active ? 'rgba(99, 102, 241, 0.08)' : 'rgba(0, 0, 0, 0.03)'};
  }

  body[data-theme='dark'] & {
    background: ${props => props.$active ? 'rgba(99, 102, 241, 0.12)' : 'transparent'};
    
    &:hover {
      background: ${props => props.$active ? 'rgba(99, 102, 241, 0.12)' : 'rgba(255, 255, 255, 0.03)'};
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
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
  
  &:hover {
    background: #fef2f2;
    color: #ef4444;
  }
`;

export const HistoryItemTitle = styled.div`
  font-size: 13px;
  font-weight: 500;
  color: #334155;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #e2e8f0;
  }
`;

export const HistoryItemTime = styled.div`
  font-size: 12px;
  color: #94a3b8;
`;

export const HistoryItemPreview = styled.div`
  font-size: 12px;
  color: #94a3b8;
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
  color: #cbd5e1;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #475569;
  }
`;

export const MessageCountBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 1px 6px;
  background: rgba(99, 102, 241, 0.08);
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
  color: #cbd5e1;
  text-align: center;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #475569;
  }
`;

export const EmptyHistoryIcon = styled.div`
  font-size: 2.5rem;
  margin-bottom: 12px;
  opacity: 0.5;
`;

export const EmptyHistoryText = styled.div`
  font-size: 13px;
  line-height: 1.6;
`;

