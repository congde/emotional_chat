import React, { useEffect, useMemo, useState } from 'react';
import styled from 'styled-components';
import { Brain, ChevronRight, HeartPulse, Lightbulb, Paperclip, Sparkles } from 'lucide-react';
import ChatAPI from '../services/ChatAPI';
import { emotionLabels } from '../constants/emotions';

const Rail = styled.aside`
  width: 300px;
  flex: 0 0 300px;
  height: 100vh;
  overflow-y: auto;
  padding: 20px 16px;
  background: var(--bg-subtle);
  border-left: 1px solid var(--border-default);

  @media (max-width: 1180px) {
    display: none;
  }
`;

const RailHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 4px 4px 18px;
  font-size: 14px;
  font-weight: 650;
`;

const Status = styled.span`
  color: var(--text-tertiary);
  font-size: 11px;
  font-weight: 500;
`;

const Card = styled.section`
  padding: 14px;
  margin-bottom: 10px;
  background: var(--bg-panel);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  transition: border-color 0.15s ease, background 0.15s ease, transform 0.15s ease;

  ${props => props.$interactive && `
    cursor: pointer;
    &:hover {
      border-color: var(--text-tertiary);
      transform: translateY(-1px);
    }
    &:focus-visible {
      outline: 2px solid var(--accent-primary);
      outline-offset: 2px;
    }
  `}
`;

const CardTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 650;
`;

const Emotion = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 650;
`;

const Dot = styled.span`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.12);
`;

const MemoryItem = styled.div`
  padding: 9px 0;
  color: var(--text-secondary);
  font-size: 12px;
  line-height: 1.5;
  border-top: 1px solid var(--border-default);

  &:first-of-type { border-top: 0; padding-top: 0; }
`;

const Suggestion = styled.button`
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 9px 0;
  background: transparent;
  border: 0;
  border-top: 1px solid var(--border-default);
  color: var(--text-secondary);
  font: inherit;
  font-size: 12px;
  text-align: left;
  cursor: pointer;

  &:first-of-type { border-top: 0; padding-top: 0; }
  &:hover { color: var(--accent-primary); }
`;

const Empty = styled.div`
  color: var(--text-tertiary);
  font-size: 12px;
  line-height: 1.5;
`;

const MemorySearch = styled.form`
  display: flex;
  gap: 6px;
  margin: 2px 0 10px;

  input {
    width: 100%;
    min-width: 0;
    height: 32px;
    padding: 0 9px;
    border: 1px solid var(--border-default);
    border-radius: 8px;
    background: var(--bg-subtle);
    color: var(--text-primary);
    outline: none;
    &:focus { border-color: var(--accent-primary); }
  }

  button {
    padding: 0 10px;
    border: 0;
    border-radius: 8px;
    background: var(--accent-primary);
    color: white;
    cursor: pointer;
  }
`;

const ActionHint = styled.span`
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  color: var(--text-tertiary);
  font-size: 11px;
  font-weight: 500;
`;

const activateOnKeyboard = (handler) => (event) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault();
    handler();
  }
};

const ContextRail = ({
  currentUserId,
  sessionId,
  messages,
  suggestions,
  attachments,
  onSuggestionClick,
  onOpenEmotionTools,
  onAddAttachment
}) => {
  const [memories, setMemories] = useState([]);
  const [memorySearchOpen, setMemorySearchOpen] = useState(false);
  const [memoryQuery, setMemoryQuery] = useState('');
  const [memorySearching, setMemorySearching] = useState(false);
  const latestEmotion = useMemo(
    () => [...messages].reverse().find((message) => message.emotion)?.emotion || 'neutral',
    [messages]
  );
  const visibleSuggestions = suggestions.length ? suggestions.slice(0, 3) : [
    '我想聊聊最近的心情',
    '带我做一次正念呼吸',
    '帮我梳理一下最近的压力'
  ];

  useEffect(() => {
    let active = true;
    ChatAPI.getUserMemories(currentUserId, 3)
      .then((result) => active && setMemories(result.memories || []))
      .catch(() => active && setMemories([]));
    return () => { active = false; };
  }, [currentUserId, sessionId, messages.length]);

  const searchMemories = async (event) => {
    event.preventDefault();
    event.stopPropagation();
    const query = memoryQuery.trim();
    if (!query || memorySearching) return;
    setMemorySearching(true);
    try {
      const result = await ChatAPI.searchUserMemories(currentUserId, query);
      setMemories(result.memories || []);
    } catch {
      setMemories([]);
    } finally {
      setMemorySearching(false);
    }
  };

  return (
    <Rail aria-label="对话上下文">
      <RailHeader>
        对话上下文
        <Status>{sessionId ? '已同步' : '新对话'}</Status>
      </RailHeader>

      <Card
        $interactive
        role="button"
        tabIndex={0}
        onClick={onOpenEmotionTools}
        onKeyDown={activateOnKeyboard(onOpenEmotionTools)}
        aria-label="打开情绪分析技能"
      >
        <CardTitle><HeartPulse size={15} /> 当前情绪 <ActionHint>查看 <ChevronRight size={13} /></ActionHint></CardTitle>
        <Emotion>
          <span>{emotionLabels[latestEmotion] || '平静'}</span>
          <Dot />
        </Emotion>
      </Card>

      <Card
        $interactive
        role="button"
        tabIndex={0}
        onClick={() => setMemorySearchOpen((open) => !open)}
        onKeyDown={activateOnKeyboard(() => setMemorySearchOpen((open) => !open))}
        aria-label="搜索相关记忆"
      >
        <CardTitle><Brain size={15} /> 相关记忆 <ActionHint>{memorySearchOpen ? '收起' : '搜索'} <ChevronRight size={13} /></ActionHint></CardTitle>
        {memorySearchOpen && (
          <MemorySearch onSubmit={searchMemories} onClick={(event) => event.stopPropagation()}>
            <input
              value={memoryQuery}
              onChange={(event) => setMemoryQuery(event.target.value)}
              placeholder="搜索真实记忆"
              aria-label="搜索记忆"
              autoFocus
            />
            <button type="submit" disabled={memorySearching}>{memorySearching ? '…' : '搜索'}</button>
          </MemorySearch>
        )}
        {memories.length ? memories.map((memory) => (
          <MemoryItem key={memory.id}>{memory.summary || memory.content}</MemoryItem>
        )) : <Empty>随着对话深入，重要信息会在这里出现。</Empty>}
      </Card>

      <Card>
        <CardTitle><Lightbulb size={15} /> 接下来可以聊</CardTitle>
        {visibleSuggestions.map((suggestion) => (
          <Suggestion key={suggestion} onClick={() => onSuggestionClick(suggestion)}>
            <span>{suggestion}</span><ChevronRight size={14} />
          </Suggestion>
        ))}
      </Card>

      <Card
        $interactive
        role="button"
        tabIndex={0}
        onClick={onAddAttachment}
        onKeyDown={activateOnKeyboard(onAddAttachment)}
        aria-label="添加附件"
      >
        <CardTitle>
          {attachments.length ? <Paperclip size={15} /> : <Sparkles size={15} />} 当前材料
          <ActionHint>添加 <ChevronRight size={13} /></ActionHint>
        </CardTitle>
        {attachments.length ? attachments.map((attachment) => (
          <MemoryItem key={attachment.id}>{attachment.name}</MemoryItem>
        )) : <Empty>本轮还没有附件或链接。</Empty>}
      </Card>
    </Rail>
  );
};

export default ContextRail;
