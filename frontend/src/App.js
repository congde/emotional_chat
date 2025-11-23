import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AppContainer } from './styles';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import FeedbackModal from './components/FeedbackModal';
import PersonalizationPanel from './components/PersonalizationPanel';
import StyleComparison from './components/StyleComparison';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import { useChat, useFileUpload, useKeyboard, useSession, useFeedback, useURLDetection } from './hooks';

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
  const [showStyleComparison, setShowStyleComparison] = useState(false);

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

  const chatHook = useChat(currentUserId);
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
    sendMessage: sendMessageHook
  } = chatHook;

  const {
    attachments,
    setAttachments,
    fileInputRef,
    handleFileUpload,
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
    await sendMessageHook(inputValue, attachments, setInputValue, setAttachments, setDetectedURLs);
    loadHistorySessions(); // 刷新历史会话列表
    setTimeout(() => inputRef.current?.focus(), 100);
  }, [inputValue, attachments, sendMessageHook, setInputValue, setAttachments, setDetectedURLs, loadHistorySessions]);

  // 新建对话
  const startNewChat = useCallback(() => {
    startNewChatHook(setMessages, setSessionId, setSuggestions, setAttachments, setDetectedURLs);
  }, [startNewChatHook, setSessionId, setMessages, setSuggestions, setAttachments, setDetectedURLs]);

  // 加载会话历史
  const handleLoadSession = useCallback((targetSessionId) => {
    loadSessionHistory(targetSessionId, setMessages, setSuggestions);
  }, [loadSessionHistory, setMessages, setSuggestions]);

  // 删除对话
  const handleDeleteSession = useCallback((targetSessionId, event) => {
    deleteConversationHook(targetSessionId, sessionId, setMessages, setSessionId, setSuggestions);
  }, [deleteConversationHook, sessionId, setSessionId, setMessages, setSuggestions]);

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

  // 如果显示样式对比页面
  if (showStyleComparison) {
    return (
      <>
        <motion.button
          onClick={() => setShowStyleComparison(false)}
          style={{
            position: 'fixed',
            top: '20px',
            left: '20px',
            zIndex: 1001,
            padding: '12px 24px',
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '2px solid #667eea',
            borderRadius: '12px',
            color: '#667eea',
            fontWeight: '600',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
          }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <X size={18} />
          返回聊天
        </motion.button>
        <StyleComparison />
      </>
    );
  }

  return (
    <AppContainer>
      <Sidebar
        currentUserId={currentUserId}
        sessionId={sessionId}
        historySessions={historySessions}
        onNewChat={startNewChat}
        onLoadSession={handleLoadSession}
        onDeleteSession={handleDeleteSession}
        onOpenPersonalization={() => setShowPersonalizationPanel(true)}
        onOpenStyleComparison={() => setShowStyleComparison(true)}
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
        onFileUpload={handleFileUpload}
        onRemoveAttachment={removeAttachment}
        onSuggestionClick={handleSuggestionClick}
        onOpenFeedbackModal={openFeedbackModal}
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
    </AppContainer>
  );
}

export default App;
