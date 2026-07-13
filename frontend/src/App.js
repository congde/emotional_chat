import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled from 'styled-components';
import { History, Plus, Settings, Zap } from 'lucide-react';
import { AppContainer } from './styles';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import FeedbackModal from './components/FeedbackModal';
import PersonalizationPanel from './components/PersonalizationPanel';
import HistoryManagementModal from './components/HistoryManagementModal';
import SkillsPanel from './components/SkillsPanel';
import ContextRail from './components/ContextRail';
import { useTheme } from './contexts/ThemeContext';
import { useChat, useFileUpload, useKeyboard, useSession, useFeedback, useURLDetection } from './hooks';

const MobileBar = styled.nav`
  display: none;
  @media (max-width: 840px) {
    position: fixed;
    inset: 0 0 auto 0;
    z-index: 50;
    height: 52px;
    padding: 7px 10px;
    display: flex;
    align-items: center;
    gap: 4px;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border-default);
  }
`;

const MobileAction = styled.button`
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 9px;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  &:hover { background: var(--bg-hover); color: var(--text-primary); }
`;

function App() {
  // 用户ID管理
  const [currentUserId] = useState(() => {
    const savedUserId = localStorage.getItem('emotional_chat_user_id');
    if (savedUserId) {
      return savedUserId;
    }
    const newUserId = `user_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    localStorage.setItem('emotional_chat_user_id', newUserId);
    return newUserId;
  });

  // UI状态
  const [inputValue, setInputValue] = useState('');
  const [showPersonalizationPanel, setShowPersonalizationPanel] = useState(false);
  const [showHistoryManagement, setShowHistoryManagement] = useState(false);
  const [showSkillsPanel, setShowSkillsPanel] = useState(false);
  const [skillsCategory, setSkillsCategory] = useState('all');
  const [deepThinkActive, setDeepThinkActive] = useState(false);
  
  // 主题管理
  const { theme, toggleTheme } = useTheme();

  const openSkills = useCallback((category = 'all') => {
    setSkillsCategory(category);
    setShowSkillsPanel(true);
  }, []);

  // Refs
  const inputRef = useRef(null);
  const attachmentButtonRef = useRef(null);
  const sendButtonRef = useRef(null);

  // 自定义Hooks
  const {
    sessionId: sessionIdFromHook,
    setSessionId: setSessionIdFromHook,
    historySessions,
    loadHistorySessions,
    loadSessionHistory,
    deleteConversation: deleteConversationHook,
    startNewChat: startNewChatHook
  } = useSession(currentUserId);

  const handleConversationSaved = useCallback((savedSessionId) => {
    setSessionIdFromHook(savedSessionId);
    loadHistorySessions();
  }, [setSessionIdFromHook, loadHistorySessions]);

  const chatHook = useChat(currentUserId, {
    onConversationSaved: handleConversationSaved
  });
  const {
    messages,
    setMessages,
    isLoading,
    sessionId: chatSessionId,
    setSessionId: setChatSessionId,
    suggestions,
    setSuggestions,
    messagesEndRef,
    scrollToBottom,
    stopGeneration,
    sendMessage: sendMessageHook
  } = chatHook;

  const {
    attachments,
    setAttachments,
    fileInputRef,
    handleFileUpload,
    addFiles,
    removeAttachment
  } = useFileUpload();

  const {
    detectedURLs,
    setDetectedURLs,
    debouncedDetectURLs
  } = useURLDetection();

  const {
    showFeedbackModal,
    feedbackType,
    feedbackRating,
    feedbackComment,
    openFeedbackModal,
    closeFeedbackModal,
    setFeedbackType,
    setFeedbackRating,
    setFeedbackComment,
    submitFeedback
  } = useFeedback(sessionIdFromHook || chatSessionId, currentUserId, messages);

  // 使用统一的sessionId
  const sessionId = sessionIdFromHook || chatSessionId;
  const setSessionId = useCallback((id) => {
    setSessionIdFromHook(id);
    setChatSessionId(id);
  }, [setSessionIdFromHook, setChatSessionId]);

  // 发送消息
  const sendMessage = useCallback(async () => {
    await sendMessageHook(inputValue, attachments, setInputValue, setAttachments, setDetectedURLs, deepThinkActive);
    // Reset textarea height after sending
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
    }
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [inputValue, attachments, sendMessageHook, setInputValue, setAttachments, setDetectedURLs, deepThinkActive]);

  // 新建对话
  const startNewChat = useCallback(() => {
    startNewChatHook(setMessages, setSessionId, setSuggestions, setAttachments, setDetectedURLs);
    setDeepThinkActive(false); // 重置深度思考状态
  }, [startNewChatHook, setSessionId, setMessages, setSuggestions, setAttachments, setDetectedURLs]);

  // 加载会话历史
  const handleLoadSession = useCallback((targetSessionId) => {
    loadSessionHistory(targetSessionId, setMessages, setSuggestions);
  }, [loadSessionHistory, setMessages, setSuggestions]);

  // 删除对话
  const handleDeleteSession = useCallback((targetSessionId, event) => {
    event?.stopPropagation();
    event?.preventDefault();
    deleteConversationHook(targetSessionId, sessionId, setMessages, setSessionId, setSuggestions);
  }, [deleteConversationHook, sessionId, setSessionId, setMessages, setSuggestions]);

  // 处理历史消息管理中的会话选择
  const handleHistorySessionSelect = useCallback((targetSessionId) => {
    loadSessionHistory(targetSessionId, setMessages, setSuggestions);
    setSessionId(targetSessionId);
  }, [loadSessionHistory, setMessages, setSuggestions, setSessionId]);

  // 处理批量删除后的回调
  const handleSessionsDeleted = useCallback((deletedSessionIds) => {
    // 如果当前会话被删除，清空消息
    if (deletedSessionIds.includes(sessionId)) {
      setMessages([]);
      setSessionId(null);
      setSuggestions([]);
    }
    // 刷新历史会话列表
    loadHistorySessions();
  }, [sessionId, setMessages, setSessionId, setSuggestions, loadHistorySessions]);

  // 键盘处理
  const { handleKeyPress, handleTabNavigation } = useKeyboard(
    startNewChat,
    sendMessage,
    inputRef,
    attachmentButtonRef,
    sendButtonRef
  );

  // 输入处理
  const handleInputChange = useCallback((e) => {
    const value = e.target.value;
    setInputValue(value);
    debouncedDetectURLs(value);

    // Auto-resize textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  }, [debouncedDetectURLs]);

  // 快捷建议点击
  const handleSuggestionClick = useCallback((suggestion) => {
    setInputValue(suggestion);
    inputRef.current?.focus();
  }, []);

  // 自动滚动
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // 应用主题到body
  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  return (
    <AppContainer>
      <MobileBar aria-label="移动导航">
        <MobileAction onClick={startNewChat} aria-label="新对话"><Plus size={18} /></MobileAction>
        <MobileAction onClick={() => setShowHistoryManagement(true)} aria-label="历史对话"><History size={18} /></MobileAction>
        <MobileAction onClick={() => openSkills('all')} aria-label="技能中心"><Zap size={18} /></MobileAction>
        <MobileAction onClick={() => setShowPersonalizationPanel(true)} aria-label="个性化"><Settings size={18} /></MobileAction>
        <span style={{ marginLeft: 'auto', fontWeight: 650, fontSize: 14, paddingRight: 8 }}>心语</span>
      </MobileBar>
      <Sidebar
        currentUserId={currentUserId}
        sessionId={sessionId}
        historySessions={historySessions}
        onNewChat={startNewChat}
        onLoadSession={handleLoadSession}
        onDeleteSession={handleDeleteSession}
        onOpenPersonalization={() => setShowPersonalizationPanel(true)}
        onOpenSkills={() => openSkills('all')}
        onToggleTheme={toggleTheme}
        theme={theme}
        onOpenHistoryManagement={() => setShowHistoryManagement(true)}
      />

      <ChatContainer
        messages={messages}
        isLoading={isLoading}
        suggestions={suggestions}
        inputValue={inputValue}
        attachments={attachments}
        detectedURLs={detectedURLs}
        messagesEndRef={messagesEndRef}
        inputRef={inputRef}
        attachmentButtonRef={attachmentButtonRef}
        sendButtonRef={sendButtonRef}
        fileInputRef={fileInputRef}
        onInputChange={handleInputChange}
        onKeyPress={handleKeyPress}
        onTabNavigation={handleTabNavigation}
        onSendMessage={sendMessage}
        onStopGeneration={stopGeneration}
        onFileUpload={handleFileUpload}
        onRemoveAttachment={removeAttachment}
        onPasteFiles={addFiles}
        onSuggestionClick={handleSuggestionClick}
        onVoiceTranscript={(transcript) => {
          setInputValue((current) => `${current}${current ? ' ' : ''}${transcript}`);
          inputRef.current?.focus();
        }}
        onOpenFeedbackModal={openFeedbackModal}
        deepThinkActive={deepThinkActive}
        onDeepThinkChange={setDeepThinkActive}
      />

      <ContextRail
        currentUserId={currentUserId}
        sessionId={sessionId}
        messages={messages}
        suggestions={suggestions}
        attachments={attachments}
        onSuggestionClick={handleSuggestionClick}
        onOpenEmotionTools={() => openSkills('emotion')}
        onAddAttachment={() => fileInputRef.current?.click()}
      />

      <PersonalizationPanel
        isOpen={showPersonalizationPanel}
        onClose={() => setShowPersonalizationPanel(false)}
        userId={currentUserId}
      />

      <FeedbackModal
        show={showFeedbackModal}
        feedbackType={feedbackType}
        feedbackRating={feedbackRating}
        feedbackComment={feedbackComment}
        onClose={closeFeedbackModal}
        onTypeChange={setFeedbackType}
        onRatingChange={setFeedbackRating}
        onCommentChange={setFeedbackComment}
        onSubmit={submitFeedback}
      />

      <HistoryManagementModal
        show={showHistoryManagement}
        onClose={() => setShowHistoryManagement(false)}
        userId={currentUserId}
        onSessionSelect={handleHistorySessionSelect}
        onSessionsDeleted={handleSessionsDeleted}
      />

      <SkillsPanel
        isOpen={showSkillsPanel}
        initialCategory={skillsCategory}
        onClose={() => setShowSkillsPanel(false)}
        onSelectSkill={(skill) => {
          const skillPrompt = `请使用“${skill.description || skill.name}”能力帮助我：`;
          setInputValue(skillPrompt);
          inputRef.current?.focus();
        }}
      />
    </AppContainer>
  );
}

export default App;
