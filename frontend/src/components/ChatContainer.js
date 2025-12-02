import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { User, Bot, Loader2, Paperclip, Send, Link, ExternalLink, X, Sparkles, Mic, PenLine, Image, Music, Languages, Presentation, MoreHorizontal } from 'lucide-react';
import {
  ChatContainer as ChatContainerStyled,
  MessagesContainer,
  MessageBubble,
  Avatar,
  MessageWrapper,
  MessageContent,
  FeedbackButtons,
  FeedbackButton,
  EmotionTag,
  MessageTimestamp,
  Suggestions,
  SuggestionChip,
  WelcomeMessage,
  LoadingIndicator,
  InputContainer
} from '../styles';
import {
  InputWrapper,
  InputBox,
  MessageInput,
  InputActions,
  LeftActions,
  RightActions,
  AttachmentButton,
  SendButton,
  FileInput,
  AttachmentsPreview,
  AttachmentItem,
  AttachmentIcon,
  RemoveAttachmentButton,
  URLPreview,
  URLText,
  URLButton,
  FeatureButton,
  QuickActions,
  QuickActionButton
} from '../styles/input';
import { emotionLabels } from '../constants/emotions';
import { formatTimestamp, formatFileSize } from '../utils/formatters';
import TypewriterComponent from './TypewriterText';
import { getFileIcon } from '../utils/fileUtils';

// 获取问候语
const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 6) return '夜深了';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 18) return '下午好';
  if (hour < 22) return '晚上好';
  return '夜深了';
};

const ChatContainer = ({
  messages,
  isLoading,
  suggestions,
  inputValue,
  attachments,
  detectedURLs,
  messagesEndRef,
  inputRef,
  attachmentButtonRef,
  sendButtonRef,
  fileInputRef,
  onInputChange,
  onKeyPress,
  onTabNavigation,
  onSendMessage,
  onFileUpload,
  onRemoveAttachment,
  onSuggestionClick,
  onOpenFeedbackModal,
  deepThinkActive,
  onDeepThinkChange
}) => {

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
    if (onTabNavigation) {
      onTabNavigation(e);
    }
  };

  return (
    <ChatContainerStyled
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <MessagesContainer>
        <AnimatePresence initial={false}>
          {messages.length === 0 ? (
            <WelcomeMessage
              key="welcome"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h3>{getGreeting()}，小草</h3>
              <p>
                我是你的情感支持伙伴，随时倾听你的心声。<br/>
                无论开心、难过还是困惑，都可以和我聊聊。
              </p>
            </WelcomeMessage>
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                isUser={message.role === 'user'}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Avatar isUser={message.role === 'user'}>
                  {message.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                </Avatar>
                <MessageWrapper>
                  <MessageContent 
                    isUser={message.role === 'user'}
                    emotion={message.emotion}
                  >
                    {message.role === 'assistant' && !message.isHistory ? (
                      <TypewriterComponent
                        text={message.content}
                        speed={30}
                        showCursor={true}
                        cursorColor="#6366f1"
                        isUser={false}
                      />
                    ) : (
                      message.content
                    )}
                    {message.emotion && message.emotion !== 'neutral' && (
                      <EmotionTag emotion={message.emotion}>
                        {emotionLabels[message.emotion] || message.emotion}
                      </EmotionTag>
                    )}
                  </MessageContent>
                  <MessageTimestamp isUser={message.role === 'user'}>
                    {formatTimestamp(message.timestamp)}
                  </MessageTimestamp>
                  {message.role === 'assistant' && (
                    <FeedbackButtons>
                      <FeedbackButton
                        onClick={() => onOpenFeedbackModal(message)}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        反馈
                      </FeedbackButton>
                    </FeedbackButtons>
                  )}
                </MessageWrapper>
              </MessageBubble>
            ))
          )}
        </AnimatePresence>

        {isLoading && (
          <LoadingIndicator
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <Loader2 size={16} className="spinner" />
            <span>正在思考中</span>
            <span className="dots">
              <span>.</span>
              <span>.</span>
              <span>.</span>
            </span>
          </LoadingIndicator>
        )}

        {suggestions.length > 0 && (
          <Suggestions>
            <AnimatePresence>
              {suggestions.map((suggestion, index) => (
                <SuggestionChip
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.05 }}
                  onClick={() => onSuggestionClick(suggestion)}
                >
                  {suggestion}
                </SuggestionChip>
              ))}
            </AnimatePresence>
          </Suggestions>
        )}

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        {/* URL预览 */}
        {detectedURLs.length > 0 && (
          <URLPreview
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Link size={14} />
            <URLText>{detectedURLs[0]}</URLText>
            <URLButton onClick={() => window.open(detectedURLs[0], '_blank')}>
              <ExternalLink size={14} />
            </URLButton>
          </URLPreview>
        )}

        {/* 附件预览 */}
        {attachments.length > 0 && (
          <AttachmentsPreview>
            <AnimatePresence>
              {attachments.map((attachment) => (
                <AttachmentItem
                  key={attachment.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                >
                  <AttachmentIcon>
                    {getFileIcon(attachment.type)}
                  </AttachmentIcon>
                  <span>{attachment.name}</span>
                  <span style={{ color: '#999' }}>({formatFileSize(attachment.size)})</span>
                  <RemoveAttachmentButton
                    onClick={() => onRemoveAttachment(attachment.id)}
                  >
                    <X size={12} />
                  </RemoveAttachmentButton>
                </AttachmentItem>
              ))}
            </AnimatePresence>
          </AttachmentsPreview>
        )}

        <InputWrapper>
          <InputBox>
            <MessageInput
              ref={inputRef}
              value={inputValue}
              onChange={onInputChange}
              onKeyDown={handleKeyDown}
              placeholder="发消息或输入 / 选择技能"
              disabled={isLoading}
              rows={1}
            />
            <InputActions>
              <LeftActions>
                <AttachmentButton
                  ref={attachmentButtonRef}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="添加附件"
                >
                  <Paperclip size={18} />
                </AttachmentButton>
                <FeatureButton
                  active={deepThinkActive}
                  onClick={() => onDeepThinkChange && onDeepThinkChange(!deepThinkActive)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Sparkles size={14} />
                  深度思考
                </FeatureButton>
              </LeftActions>
              <RightActions>
                <AttachmentButton
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="语音输入"
                >
                  <Mic size={18} />
                </AttachmentButton>
                <SendButton
                  ref={sendButtonRef}
                  onClick={onSendMessage}
                  disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title="发送消息"
                >
                  <Send size={16} />
                </SendButton>
              </RightActions>
            </InputActions>
          </InputBox>

        </InputWrapper>

        <FileInput
          ref={fileInputRef}
          type="file"
          multiple
          accept="image/*,application/pdf,.doc,.docx,.txt"
          onChange={onFileUpload}
        />
      </InputContainer>
    </ChatContainerStyled>
  );
};

export default ChatContainer;

