import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { Plus, Clock, Settings, Palette, User, Trash2 } from 'lucide-react';
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
  HistoryItemTime,
  HistoryItemPreview,
  HistoryItemMeta,
  MessageCountBadge,
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
  onOpenStyleComparison
}) => {
  return (
    <SidebarStyled
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <SidebarHeader>
        <UserAvatar>
          <User size={20} />
        </UserAvatar>
        <UserName>情感伙伴</UserName>
      </SidebarHeader>

      <NewChatButton
        onClick={onNewChat}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Plus size={16} />
        新对话
      </NewChatButton>

      <SettingsButton
        onClick={onOpenPersonalization}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Settings size={16} />
        个性化配置
      </SettingsButton>

      <SettingsButton
        onClick={onOpenStyleComparison}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Palette size={16} />
        样式对比演示
      </SettingsButton>

      <HistorySection>
        <HistoryTitle>
          <Clock size={16} />
          历史对话
        </HistoryTitle>
        <HistoryList>
          {historySessions.length === 0 ? (
            <EmptyHistoryState>
              <EmptyHistoryIcon>💬</EmptyHistoryIcon>
              <EmptyHistoryText>
                <div style={{ fontWeight: 600, marginBottom: 8 }}>还没有历史对话</div>
                <div>开始一段新的对话吧！</div>
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
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                >
                  <HistoryItemContent>
                    <HistoryItemTitle>{session.title || '新对话'}</HistoryItemTitle>
                    {session.preview && (
                      <HistoryItemPreview>{session.preview}</HistoryItemPreview>
                    )}
                    <HistoryItemMeta>
                      <HistoryItemTime>
                        {formatRelativeTime(session.updated_at)}
                      </HistoryItemTime>
                      {session.message_count !== undefined && session.message_count > 0 && (
                        <>
                          <span>•</span>
                          <MessageCountBadge>
                            {session.message_count} 条消息
                          </MessageCountBadge>
                        </>
                      )}
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

