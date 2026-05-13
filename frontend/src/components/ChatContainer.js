import React, { useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { User, Bot, Loader2, Paperclip, Send, Link, ExternalLink, X, Sparkles, Mic, Heart, MessageCircle, Brain, Smile } from 'lucide-react';
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
import styled from 'styled-components';

// WorkBuddy-style welcome components
const WelcomeContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  padding: 40px 20px;
  max-width: 680px;
  margin: 0 auto;
  width: 100%;
`;

const WelcomeAvatar = styled.div`
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: linear-gradient(135deg, #6366f1 0%, #a78bfa 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(99, 102, 241, 0.25);
`;

const WelcomeTitle = styled.h2`
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
  text-align: center;
  
  body[data-theme='dark'] & {
    color: #f1f5f9;
  }
`;

const WelcomeSubtitle = styled.p`
  font-size: 15px;
  color: #94a3b8;
  margin-bottom: 36px;
  text-align: center;
  line-height: 1.6;
  
  body[data-theme='dark'] & {
    color: #64748b;
  }
`;

const QuickStartGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  width: 100%;
  
  @media (max-width: 520px) {
    grid-template-columns: 1fr;
  }
`;

const QuickStartCard = styled.button`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 16px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  
  &:hover {
    border-color: rgba(99, 102, 241, 0.2);
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.08);
    transform: translateY(-2px);
  }
  
  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.06);
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.2);
    
    &:hover {
      border-color: rgba(99, 102, 241, 0.3);
      box-shadow: 0 4px 16px rgba(99, 102, 241, 0.15);
    }
  }
`;

const CardIcon = styled.div`
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: ${props => props.$bg || 'rgba(99, 102, 241, 0.08)'};
  color: ${props => props.$color || '#6366f1'};
`;

const CardContent = styled.div`
  flex: 1;
  min-width: 0;
`;

const CardTitle = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
  
  body[data-theme='dark'] & {
    color: #e2e8f0;
  }
`;

const CardDesc = styled.div`
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  
  body[data-theme='dark'] & {
    color: #64748b;
  }
`;

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

const quickStartItems = [
  {
    icon: <Heart size={18} />,
    bg: 'rgba(239, 68, 68, 0.08)',
    color: '#ef4444',
    title: '情感倾诉',
    desc: '聊聊最近的心情和感受',
    message: '我想聊聊最近的心情'
  },
  {
    icon: <Brain size={18} />,
    bg: 'rgba(99, 102, 241, 0.08)',
    color: '#6366f1',
    title: '心理调适',
    desc: '获得科学的心理健康建议',
    message: '最近压力有点大，有什么好的调节方法吗？'
  },
  {
    icon: <MessageCircle size={18} />,
    bg: 'rgba(16, 185, 129, 0.08)',
    color: '#10b981',
    title: '日常对话',
    desc: '轻松地聊天，放松心情',
    message: '你好，今天过得怎么样？'
  },
  {
    icon: <Smile size={18} />,
    bg: 'rgba(245, 158, 11, 0.08)',
    color: '#f59e0b',
    title: '正念练习',
    desc: '一起做呼吸和冥想练习',
    message: '可以带我做一个正念呼吸练习吗？'
  }
];

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
            <WelcomeContainer>
              <WelcomeAvatar>
                <Heart size={28} />
              </WelcomeAvatar>
              <WelcomeTitle>{getGreeting()}，我是心语</WelcomeTitle>
              <WelcomeSubtitle>
                你的AI情感支持伙伴，随时倾听你的心声
              </WelcomeSubtitle>
              <QuickStartGrid>
                {quickStartItems.map((item, index) => (
                  <QuickStartCard
                    key={index}
                    onClick={() => {
                      onSuggestionClick(item.message);
                    }}
                  >
                    <CardIcon $bg={item.bg} $color={item.color}>
                      {item.icon}
                    </CardIcon>
                    <CardContent>
                      <CardTitle>{item.title}</CardTitle>
                      <CardDesc>{item.desc}</CardDesc>
                    </CardContent>
                  </QuickStartCard>
                ))}
              </QuickStartGrid>
            </WelcomeContainer>
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
                    {message.role === 'assistant' ? (
                      message.streaming ? (
                        <>
                          {message.content}
                          <span className="streaming-cursor" style={{
                            display: 'inline-block',
                            width: '2px',
                            height: '1em',
                            background: '#6366f1',
                            marginLeft: '2px',
                            animation: 'blink 0.8s infinite',
                            verticalAlign: 'text-bottom'
                          }} />
                        </>
                      ) : message.isHistory ? (
                        message.content
                      ) : (
                        <TypewriterComponent
                          text={message.content}
                          speed={30}
                          showCursor={true}
                          cursorColor="#6366f1"
                          isUser={false}
                        />
                      )
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

        {isLoading && !messages.some(m => m.streaming && m.content) && (
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
                  $active={deepThinkActive}
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

