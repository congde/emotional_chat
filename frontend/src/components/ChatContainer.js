import React, { useRef, useState } from 'react';
import { AnimatePresence } from 'framer-motion';
import { User, Bot, Loader2, Paperclip, Send, Square, Link, ExternalLink, X, Sparkles, Mic, Heart, MessageCircle, Brain, Smile } from 'lucide-react';
import {
  ChatContainer as ChatContainerStyled,
  ChatHeader,
  ChatTitle,
  ChatSubtitle,
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
} from '../styles/input';
import { emotionLabels } from '../constants/emotions';
import { formatTimestamp, formatFileSize } from '../utils/formatters';
import MarkdownRenderer from './MarkdownRenderer';
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
  width: 52px;
  height: 52px;
  border-radius: 16px;
  background: var(--bg-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  margin-bottom: 20px;
  box-shadow: none;
`;

const WelcomeTitle = styled.h2`
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
  text-align: center;
  
  body[data-theme='dark'] & {
    color: #f1f5f9;
  }
`;

const WelcomeSubtitle = styled.p`
  font-size: 15px;
  color: var(--text-secondary);
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
  background: var(--bg-panel);
  border: 1px solid var(--border-default);
  border-radius: 12px;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
  box-shadow: none;
  
  &:hover {
    border-color: var(--text-tertiary);
    background: var(--bg-subtle);
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

const ImageThumbnail = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 8px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s ease;
  border: 1px solid rgba(0, 0, 0, 0.08);
  
  &:hover {
    transform: scale(1.1);
  }

  body[data-theme='dark'] & {
    border-color: rgba(255, 255, 255, 0.1);
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
  onStopGeneration,
  onFileUpload,
  onRemoveAttachment,
  onPasteFiles,
  onSuggestionClick,
  onVoiceTranscript,
  onOpenFeedbackModal,
  deepThinkActive,
  onDeepThinkChange
}) => {
  const isComposingRef = useRef(false);
  const recognitionRef = useRef(null);
  const [isListening, setIsListening] = useState(false);

  const toggleVoiceInput = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      return;
    }

    const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!Recognition) {
      window.alert('当前浏览器不支持语音输入，请使用最新版 Chrome 或 Edge。');
      return;
    }

    const recognition = new Recognition();
    recognition.lang = 'zh-CN';
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };
    recognition.onerror = (event) => {
      setIsListening(false);
      recognitionRef.current = null;
      if (event.error !== 'aborted') {
        window.alert(`语音识别失败：${event.error || '未知错误'}`);
      }
    };
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0]?.transcript || '')
        .join('')
        .trim();
      if (transcript) onVoiceTranscript?.(transcript);
    };
    recognitionRef.current = recognition;
    recognition.start();
  };

  // 处理粘贴事件 - 支持粘贴图片
  const handlePaste = (e) => {
    const clipboardItems = e.clipboardData?.items;
    if (!clipboardItems) return;

    const imageFiles = [];
    for (let i = 0; i < clipboardItems.length; i++) {
      const item = clipboardItems[i];
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          // 为粘贴的图片生成文件名
          const ext = item.type.split('/')[1] || 'png';
          const namedFile = new File([file], `粘贴图片_${Date.now()}.${ext}`, { type: item.type });
          imageFiles.push(namedFile);
        }
      }
    }

    if (imageFiles.length > 0) {
      e.preventDefault();
      onPasteFiles?.(imageFiles);
    }
  };

  const handleKeyDown = (e) => {
    const isComposing =
      isComposingRef.current ||
      e.nativeEvent?.isComposing ||
      e.isComposing ||
      e.keyCode === 229;

    if (isComposing) {
      return;
    }

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
      <ChatHeader>
        <div>
          <ChatTitle>心语对话</ChatTitle>
          <ChatSubtitle>安全、私密的情感陪伴空间</ChatSubtitle>
        </div>
        <div style={{ color: 'var(--text-tertiary)', fontSize: 12 }}>重要决定请谨慎核实</div>
      </ChatHeader>
      <MessagesContainer>
        <AnimatePresence initial={false}>
          {messages.length === 0 ? (
            <WelcomeContainer>
              <WelcomeAvatar>
                <Heart size={28} />
              </WelcomeAvatar>
              <WelcomeTitle>今天想聊些什么？</WelcomeTitle>
              <WelcomeSubtitle>
                {getGreeting()}。我会认真倾听，也会记住对你重要的事情。
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
                          <MarkdownRenderer content={message.content} />
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
                      ) : (
                        <MarkdownRenderer content={message.content} />
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
                  $isImage={attachment.type?.startsWith('image/')}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                >
                  {attachment.type?.startsWith('image/') && attachment.previewUrl ? (
                    <ImageThumbnail
                      src={attachment.previewUrl}
                      alt={attachment.name}
                      onClick={() => {
                        if (attachment.previewUrl) window.open(attachment.previewUrl, '_blank');
                      }}
                    />
                  ) : (
                    <AttachmentIcon>
                      {getFileIcon(attachment.type)}
                    </AttachmentIcon>
                  )}
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
              onPaste={handlePaste}
              onCompositionStart={() => {
                isComposingRef.current = true;
              }}
              onCompositionEnd={() => {
                isComposingRef.current = false;
              }}
              placeholder="发消息或输入 / 选择技能，可粘贴图片"
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
                  onClick={toggleVoiceInput}
                  $active={isListening}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title={isListening ? '停止语音输入' : '语音输入'}
                  aria-label={isListening ? '停止语音输入' : '开始语音输入'}
                >
                  <Mic size={18} />
                </AttachmentButton>
                <SendButton
                  ref={sendButtonRef}
                  onClick={isLoading ? onStopGeneration : onSendMessage}
                  disabled={!isLoading && !inputValue.trim() && attachments.length === 0}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  title={isLoading ? '停止生成' : '发送消息'}
                >
                  {isLoading ? <Square size={14} fill="currentColor" /> : <Send size={16} />}
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

