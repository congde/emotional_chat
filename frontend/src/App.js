import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Heart, MessageCircle, User, Bot, Loader2 } from 'lucide-react';
import ChatAPI from './services/ChatAPI';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
`;

const ChatContainer = styled(motion.div)`
  width: 100%;
  max-width: 800px;
  height: 80vh;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(10px);
`;

const Header = styled.div`
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  padding: 20px;
  text-align: center;
  position: relative;
`;

const Title = styled.h1`
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
`;

const Subtitle = styled.p`
  font-size: 0.9rem;
  opacity: 0.9;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const MessageBubble = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 10px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${props => props.isUser ? '#667eea' : '#ff6b6b'};
  color: white;
  flex-shrink: 0;
`;

const MessageContent = styled.div`
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  background: ${props => props.isUser ? '#667eea' : '#f8f9fa'};
  color: ${props => props.isUser ? 'white' : '#333'};
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 10px;
    ${props => props.isUser ? 'right: -8px;' : 'left: -8px;'}
    width: 0;
    height: 0;
    border: 8px solid transparent;
    border-${props => props.isUser ? 'left' : 'right'}-color: ${props => props.isUser ? '#667eea' : '#f8f9fa'};
  }
`;

const EmotionTag = styled.span`
  display: inline-block;
  background: ${props => {
    const colors = {
      happy: '#ffd93d',
      sad: '#74b9ff',
      angry: '#fd79a8',
      anxious: '#a29bfe',
      excited: '#fdcb6e',
      confused: '#6c5ce7',
      frustrated: '#e84393',
      lonely: '#636e72',
      grateful: '#00b894',
      neutral: '#b2bec3'
    };
    return colors[props.emotion] || colors.neutral;
  }};
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  margin-left: 8px;
  font-weight: 500;
`;

const Suggestions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
`;

const SuggestionChip = styled(motion.button)`
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(102, 126, 234, 0.2);
    transform: translateY(-1px);
  }
`;

const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 10px;
  align-items: center;
`;

const MessageInput = styled.input`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 25px;
  font-size: 1rem;
  outline: none;
  transition: all 0.2s ease;
  
  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SendButton = styled(motion.button)`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    transform: scale(1.05);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const LoadingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 0.9rem;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 18px;
  max-width: 200px;
  margin: 0 auto;
`;

const WelcomeMessage = styled(motion.div)`
  text-align: center;
  color: #666;
  padding: 40px 20px;
  
  h3 {
    margin-bottom: 10px;
    color: #333;
  }
  
  p {
    line-height: 1.6;
  }
`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue('');
    setIsLoading(true);

    // 添加用户消息
    const newUserMessage = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await ChatAPI.sendMessage({
        message: userMessage,
        session_id: sessionId
      });

      setSessionId(response.session_id);
      setSuggestions(response.suggestions || []);

      // 添加机器人回复
      const botMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.response,
        emotion: response.emotion,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('发送消息失败:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '抱歉，我现在无法回应。请稍后再试。',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInputValue(suggestion);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <AppContainer>
      <ChatContainer
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
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
          <AnimatePresence>
            {messages.length === 0 ? (
              <WelcomeMessage
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
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
                  transition={{ duration: 0.3 }}
                >
                  <Avatar isUser={message.role === 'user'}>
                    {message.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                  </Avatar>
                  <MessageContent isUser={message.role === 'user'}>
                    {message.content}
                    {message.emotion && message.emotion !== 'neutral' && (
                      <EmotionTag emotion={message.emotion}>
                        {message.emotion}
                      </EmotionTag>
                    )}
                  </MessageContent>
                </MessageBubble>
              ))
            )}
          </AnimatePresence>

          {isLoading && (
            <LoadingIndicator
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <Loader2 size={16} className="animate-spin" />
              正在思考中...
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
                    onClick={() => handleSuggestionClick(suggestion)}
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
          <MessageInput
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="分享你的想法和感受..."
            disabled={isLoading}
          />
          <SendButton
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Send size={20} />
          </SendButton>
        </InputContainer>
      </ChatContainer>
    </AppContainer>
  );
}

export default App;
