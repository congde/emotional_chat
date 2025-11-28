import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { Plus, Clock, Settings, Moon, Sun, Trash2, FolderOpen } from 'lucide-react';
import { Sidebar as SidebarStyled } from '../styles/layout';
import {
  SidebarHeader,
  UserAvatar,
  UserName,
  NewChatButton,
  SettingsButton,
  HistorySection,
  HistoryTitle,
  HistoryList,
  HistoryItem,
  HistoryItemContent,
  HistoryItemActions,
  DeleteButton,
  HistoryItemTitle,
  HistoryItemMeta,
  EmptyHistoryState,
  EmptyHistoryIcon,
  EmptyHistoryText
} from '../styles/sidebar';
import { formatRelativeTime } from '../utils/formatters';

const Sidebar = ({
  currentUserId,
  sessionId,
  historySessions,
  onNewChat,
  onLoadSession,
  onDeleteSession,
  onOpenPersonalization,
  onToggleTheme,
  theme,
  onOpenHistoryManagement
}) => {
  return (
    <SidebarStyled
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <SidebarHeader>
        <UserAvatar>🤖</UserAvatar>
        <UserName>情感聊天</UserName>
      </SidebarHeader>

      <NewChatButton
        onClick={onNewChat}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <Plus size={16} />
        新对话
      </NewChatButton>

      <SettingsButton
        onClick={onOpenPersonalization}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <Settings size={16} />
        个性化配置
      </SettingsButton>

      <SettingsButton
        onClick={onToggleTheme}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        {theme === 'dark' ? '浅色模式' : '深色模式'}
      </SettingsButton>

      <HistorySection>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <HistoryTitle>
            <Clock size={14} />
            历史对话
          </HistoryTitle>
          {historySessions.length > 0 && onOpenHistoryManagement && (
            <button
              onClick={onOpenHistoryManagement}
              style={{
                padding: '4px 8px',
                fontSize: '12px',
                background: 'transparent',
                color: '#888',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
              title="管理对话记录"
            >
              <FolderOpen size={12} />
              管理
            </button>
          )}
        </div>
        <HistoryList>
          {historySessions.length === 0 ? (
            <EmptyHistoryState>
              <EmptyHistoryIcon>💬</EmptyHistoryIcon>
              <EmptyHistoryText>
                <div style={{ fontWeight: 500, marginBottom: 4 }}>还没有历史对话</div>
                <div>开始一段新的对话吧</div>
              </EmptyHistoryText>
            </EmptyHistoryState>
          ) : (
            <AnimatePresence>
              {historySessions.map((session) => (
                <HistoryItem
                  key={session.session_id}
                  active={session.session_id === sessionId}
                  onClick={(e) => {
                    e.stopPropagation();
                    e.preventDefault();
                    onLoadSession(session.session_id);
                  }}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  transition={{ duration: 0.15 }}
                >
                  <HistoryItemContent>
                    <HistoryItemTitle>{session.title || '新对话'}</HistoryItemTitle>
                    <HistoryItemMeta>
                      <span>{formatRelativeTime(session.updated_at)}</span>
                    </HistoryItemMeta>
                  </HistoryItemContent>
                  <HistoryItemActions>
                    <DeleteButton
                      onClick={(e) => onDeleteSession(session.session_id, e)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      title="删除对话"
                    >
                      <Trash2 size={14} />
                    </DeleteButton>
                  </HistoryItemActions>
                </HistoryItem>
              ))}
            </AnimatePresence>
          )}
        </HistoryList>
      </HistorySection>
    </SidebarStyled>
  );
};

export default Sidebar;

