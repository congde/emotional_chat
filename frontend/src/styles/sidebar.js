import styled from 'styled-components';
import { motion } from 'framer-motion';

export const SidebarHeader = styled.div`
  padding: 18px 16px 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 0;
  transition: border-color 0.3s ease;

  body[data-theme='dark'] & {
    border-bottom-color: rgba(255, 255, 255, 0.06);
  }
`;

export const UserAvatar = styled.div`
  width: 28px;
  height: 28px;
  border-radius: 9px;
  background: #202327;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
  box-shadow: none;
`;

export const UserName = styled.div`
  font-weight: 700;
  color: var(--text-primary);
  font-size: 16px;
  letter-spacing: -0.3px;
  transition: color 0.3s ease;

  body[data-theme='dark'] & {
    color: #f1f5f9;
  }
`;

export const NewChatButton = styled(motion.button)`
  margin: 6px 12px 8px;
  background: var(--bg-panel);
  color: var(--text-primary);
  border: 1px solid var(--border-default);
  padding: 10px 12px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
  
  &:hover {
    background: var(--bg-hover);
    box-shadow: none;
  }
`;

export const SettingsButton = styled(motion.button)`
  margin: 0 12px 2px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 9px 10px;
  border-radius: 9px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
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
  color: var(--text-tertiary);
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
  background: ${props => props.$active ? 'var(--bg-hover)' : 'transparent'};
  border-left: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  
  &:hover {
    background: var(--bg-hover);
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

