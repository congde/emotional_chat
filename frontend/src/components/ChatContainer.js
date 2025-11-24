import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { Heart, User, Bot, Loader2, Paperclip, Send, Link, ExternalLink, X, MessageSquarePlus } from 'lucide-react';
import {
  ChatContainer as ChatContainerStyled,
  Header,
  Title,
  Subtitle,
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
  InputContainer,
  InputRow,
  MessageInput,
  AttachmentButton,
  SendButton,
  FileInput,
  AttachmentsPreview,
  AttachmentItem,
  AttachmentIcon,
  RemoveAttachmentButton,
  URLPreview,
  URLText,
  URLButton
} from '../styles';
import { emotionLabels } from '../constants/emotions';
import { formatTimestamp, formatFileSize } from '../utils/formatters';
import TypewriterComponent from './TypewriterText';
import { getFileIcon } from '../utils/fileUtils';

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
  onOpenFeedbackModal
}) => {
  return (
    <ChatContainerStyled
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Header>
        <Title>
          <Heart size={24} />
          情感聊天机器人
        </Title>
        <Subtitle>温暖陪伴，理解倾听</Subtitle>
      </Header>

      <MessagesContainer>
        <AnimatePresence initial={false}>
          {messages.length === 0 ? (
            <WelcomeMessage
              key="welcome"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h3>👋 你好！我是你的情感支持伙伴</h3>
              <p>
                我在这里倾听你的心声，理解你的感受。<br/>
                无论是开心、难过、焦虑还是困惑，我都愿意陪伴你。<br/>
                请随意分享你的想法和感受吧！
              </p>
            </WelcomeMessage>
          ) : (
            messages.map((message) => (
              <MessageBubble
                key={message.id}
                isUser={message.role === 'user'}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Avatar isUser={message.role === 'user'}>
                  {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </Avatar>
                <MessageWrapper>
                  <MessageContent 
                    isUser={message.role === 'user'}
                    emotion={message.emotion}
                  >
                    {message.role === 'assistant' && !message.isHistory ? (
                      <TypewriterComponent
                        text={message.content}
                        speed={message.emotion === 'sad' ? 40 : message.emotion === 'angry' ? 20 : message.emotion === 'happy' ? 25 : 30}
                        showCursor={true}
                        cursorColor={message.emotion === 'sad' ? '#74b9ff' : message.emotion === 'angry' ? '#ff7675' : message.emotion === 'happy' ? '#00b894' : '#333'}
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
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <MessageSquarePlus size={14} />
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
            exit={{ opacity: 0, y: -10 }}
          >
            <Loader2 size={18} className="spinner" />
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
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  transition={{ delay: index * 0.1 }}
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
            <Link size={16} />
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
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                >
                  <AttachmentIcon>
                    {getFileIcon(attachment.type)}
                  </AttachmentIcon>
                  <span>{attachment.name}</span>
                  <span>({formatFileSize(attachment.size)})</span>
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

        <InputRow>
          <MessageInput
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={onInputChange}
            onKeyPress={onKeyPress}
            onKeyDown={onTabNavigation}
            placeholder="分享你的想法和感受..."
            disabled={isLoading}
            aria-label="消息输入框"
            aria-describedby="input-hint"
          />
          <AttachmentButton
            ref={attachmentButtonRef}
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading}
            onKeyDown={onTabNavigation}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label="添加附件"
            title="添加附件 (图片、PDF、文档)"
          >
            <Paperclip size={20} />
          </AttachmentButton>
          <SendButton
            ref={sendButtonRef}
            onClick={onSendMessage}
            disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
            onKeyDown={onTabNavigation}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            aria-label="发送消息"
            aria-disabled={(!inputValue.trim() && attachments.length === 0) || isLoading}
            title="发送消息 (Enter)"
          >
            <Send size={20} />
          </SendButton>
        </InputRow>

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

