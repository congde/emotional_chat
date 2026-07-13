import React, { useMemo, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { Plus, Clock, Settings, Moon, Sun, Trash2, FolderOpen, Heart, Zap, Search, Brain } from 'lucide-react';
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
  onOpenSkills,
  onToggleTheme,
  theme,
  onOpenHistoryManagement
}) => {
  const [query, setQuery] = useState('');
  const visibleSessions = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return historySessions;
    return historySessions.filter((session) =>
      `${session.title || ''} ${session.preview || ''}`.toLowerCase().includes(keyword)
    );
  }, [historySessions, query]);
  const groupedSessions = useMemo(() => {
    const now = new Date();
    const groups = { '今天': [], '昨天': [], '近 7 天': [], '更早': [] };
    visibleSessions.forEach((session) => {
      const date = new Date(session.updated_at || session.created_at);
      const days = Math.floor((now - date) / 86400000);
      const label = days <= 0 ? '今天' : days === 1 ? '昨天' : days <= 7 ? '近 7 天' : '更早';
      groups[label].push(session);
    });
    return Object.entries(groups).filter(([, sessions]) => sessions.length);
  }, [visibleSessions]);

  return (
    <SidebarStyled
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <SidebarHeader>
        <UserAvatar><Heart size={16} /></UserAvatar>
        <UserName>心语</UserName>
      </SidebarHeader>

      <NewChatButton
        onClick={onNewChat}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <Plus size={16} />
        新对话
      </NewChatButton>

      <div style={{ position: 'relative', margin: '2px 12px 10px' }}>
        <Search size={15} style={{ position: 'absolute', left: 11, top: 10, color: 'var(--text-tertiary)' }} />
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="搜索对话"
          aria-label="搜索历史对话"
          style={{
            width: '100%', height: 35, padding: '0 10px 0 34px', borderRadius: 9,
            border: '1px solid var(--border-default)', background: 'var(--bg-panel)',
            color: 'var(--text-primary)', outline: 'none', font: 'inherit', fontSize: 13
          }}
        />
      </div>

      <SettingsButton
        onClick={onOpenPersonalization}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <Settings size={16} />
        个性化配置
      </SettingsButton>

      <SettingsButton
        onClick={onOpenSkills}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <Zap size={16} />
        技能中心
      </SettingsButton>

      <SettingsButton onClick={onOpenHistoryManagement}>
        <Brain size={16} />
        历史管理
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
                color: '#94a3b8',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                transition: 'color 0.2s',
              }}
              title="管理对话记录"
            >
              <FolderOpen size={12} />
              管理
            </button>
          )}
        </div>
        <HistoryList>
          {visibleSessions.length === 0 ? (
            <EmptyHistoryState>
              <EmptyHistoryIcon>💬</EmptyHistoryIcon>
              <EmptyHistoryText>
                <div style={{ fontWeight: 500, marginBottom: 4 }}>还没有历史对话</div>
                <div>开始一段新的对话吧</div>
              </EmptyHistoryText>
            </EmptyHistoryState>
          ) : (
            groupedSessions.map(([group, sessions]) => (
              <div key={group}>
                <div style={{ padding: '10px 12px 4px', fontSize: 10, fontWeight: 650, color: 'var(--text-tertiary)' }}>{group}</div>
                <AnimatePresence>
                {sessions.map((session) => (
                <HistoryItem
                  key={session.session_id}
                  $active={session.session_id === sessionId}
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
              </div>
            ))
          )}
        </HistoryList>
      </HistorySection>
    </SidebarStyled>
  );
};

export default Sidebar;

