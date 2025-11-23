import React, { useState } from 'react';
import styled, { keyframes } from 'styled-components';
import { motion } from 'framer-motion';
import { Heart, MessageSquare, User, Bot, Palette, Layers } from 'lucide-react';

// 旋转动画
const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

// ========== 有特效版本（温暖氛围） ==========
const EnhancedContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  background-size: 200% 200%;
  animation: gradientShift 15s ease infinite;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  position: relative;
  overflow: hidden;

  @keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
  }

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: ${spin} 20s linear infinite;
    pointer-events: none;
  }
`;

const EnhancedCard = styled(motion.div)`
  width: 90%;
  max-width: 800px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 40px;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.5) inset,
    0 0 100px rgba(102, 126, 234, 0.2);
  position: relative;
  z-index: 1;
  border: 1px solid rgba(255, 255, 255, 0.3);

  @media (max-width: 768px) {
    padding: 24px;
    border-radius: 16px;
  }
`;

const EnhancedHeader = styled.div`
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  padding: 24px;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 8px 24px rgba(255, 107, 107, 0.3);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 1px, transparent 1px);
    background-size: 30px 30px;
    animation: ${spin} 15s linear infinite;
  }
`;

const EnhancedMessage = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const EnhancedAvatar = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: ${props => props.isUser 
    ? 'linear-gradient(135deg, #667eea, #764ba2)' 
    : 'linear-gradient(135deg, #ff6b6b, #ff8e8e)'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
`;

const EnhancedBubble = styled.div`
  max-width: 70%;
  padding: 16px 20px;
  border-radius: 20px;
  background: ${props => props.isUser 
    ? 'linear-gradient(135deg, #667eea, #764ba2)' 
    : 'rgba(248, 249, 250, 0.9)'};
  backdrop-filter: blur(10px);
  color: ${props => props.isUser ? 'white' : '#333'};
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset;
  position: relative;
  line-height: 1.6;

  &::before {
    content: '';
    position: absolute;
    top: 12px;
    ${props => props.isUser ? 'right: -8px;' : 'left: -8px;'}
    width: 0;
    height: 0;
    border: 8px solid transparent;
    border-${props => props.isUser ? 'left' : 'right'}-color: ${props => props.isUser 
      ? '#667eea' 
      : 'rgba(248, 249, 250, 0.9)'};
  }
`;

const EnhancedButton = styled(motion.button)`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  margin-top: 20px;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
  }
`;

// ========== 无特效版本（传统风格） ==========
const PlainContainer = styled.div`
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
`;

const PlainCard = styled.div`
  width: 90%;
  max-width: 800px;
  background: #ffffff;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;

  @media (max-width: 768px) {
    padding: 24px;
  }
`;

const PlainHeader = styled.div`
  background: #e0e0e0;
  color: #333;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 24px;
  border: 1px solid #d0d0d0;
`;

const PlainMessage = styled.div`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  ${props => props.isUser ? 'flex-direction: row-reverse;' : ''}
`;

const PlainAvatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${props => props.isUser ? '#667eea' : '#ff6b6b'};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
`;

const PlainBubble = styled.div`
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 8px;
  background: ${props => props.isUser ? '#667eea' : '#f0f0f0'};
  color: ${props => props.isUser ? 'white' : '#333'};
  border: 1px solid ${props => props.isUser ? '#5568d3' : '#e0e0e0'};
  line-height: 1.5;
`;

const PlainButton = styled.button`
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 20px;

  &:hover {
    background: #5568d3;
  }
`;

// ========== 通用样式 ==========
const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: ${props => props.enhanced ? 'white' : '#333'};
`;

const Subtitle = styled.p`
  font-size: 1rem;
  opacity: ${props => props.enhanced ? 0.95 : 0.7};
  color: ${props => props.enhanced ? 'white' : '#666'};
`;

const ComparisonContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 40px;
  width: 100%;
  max-width: 1800px;
  margin: 0 auto;
`;

const ComparisonRow = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  width: 100%;

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
    gap: 40px;
  }
`;

const SectionTitle = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  font-size: 1.5rem;
  font-weight: 600;
  color: ${props => props.enhanced ? 'white' : '#333'};
`;

const FeatureList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const FeatureItem = styled.li`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  color: ${props => props.enhanced ? 'rgba(255, 255, 255, 0.9)' : '#666'};
  font-size: 0.95rem;
`;

const ToggleContainer = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  padding: 12px 20px;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
`;

const ToggleButton = styled.button`
  padding: 8px 16px;
  border-radius: 8px;
  border: 2px solid ${props => props.active ? '#667eea' : '#e0e0e0'};
  background: ${props => props.active ? 'rgba(102, 126, 234, 0.1)' : 'transparent'};
  color: ${props => props.active ? '#667eea' : '#666'};
  font-weight: ${props => props.active ? '600' : '500'};
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
  }
`;

const InfoBox = styled.div`
  background: ${props => props.enhanced 
    ? 'rgba(255, 255, 255, 0.15)' 
    : '#f8f9fa'};
  backdrop-filter: ${props => props.enhanced ? 'blur(10px)' : 'none'};
  border: 1px solid ${props => props.enhanced 
    ? 'rgba(255, 255, 255, 0.3)' 
    : '#e0e0e0'};
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
  color: ${props => props.enhanced ? 'rgba(255, 255, 255, 0.95)' : '#666'};
`;

function StyleComparison() {
  const [viewMode, setViewMode] = useState('comparison'); // 'comparison' | 'enhanced' | 'plain'

  const sampleMessages = [
    { role: 'user', content: '你好，我最近感觉压力很大...' },
    { role: 'assistant', content: '我理解你的感受。压力是生活中常见的情绪，让我们一起面对它。你可以告诉我具体是什么让你感到压力吗？' },
    { role: 'user', content: '工作上的事情，还有人际关系...' },
    { role: 'assistant', content: '听起来你同时面临多个挑战。这确实不容易。让我们一步步来，先从工作上的压力开始，好吗？' }
  ];

  const enhancedFeatures = [
    '✨ 渐变色背景营造温暖氛围',
    '🔮 毛玻璃效果（backdrop-filter）增加层次感',
    '💫 微妙的动画和过渡效果',
    '🌈 情感化的色彩搭配',
    '✨ 柔和的阴影和光晕效果',
    '🎨 现代化的圆角和间距设计'
  ];

  const plainFeatures = [
    '⚪ 纯色背景，简洁明了',
    '📦 实心卡片，无透明效果',
    '🔲 传统边框和阴影',
    '⚫ 标准色彩方案',
    '📐 规整的布局设计',
    '💼 商务风格，专业感强'
  ];

  const renderEnhanced = () => (
    <EnhancedContainer>
      <EnhancedCard
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <EnhancedHeader>
          <Title enhanced>
            <Heart size={28} />
            情感聊天机器人
          </Title>
          <Subtitle enhanced>温暖陪伴，理解倾听</Subtitle>
        </EnhancedHeader>

        <SectionTitle enhanced>
          <Palette size={24} />
          有特效版本（温暖氛围）
        </SectionTitle>

        <div>
          {sampleMessages.map((msg, idx) => (
            <EnhancedMessage key={idx} isUser={msg.role === 'user'}>
              <EnhancedAvatar isUser={msg.role === 'user'}>
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </EnhancedAvatar>
              <EnhancedBubble isUser={msg.role === 'user'}>
                {msg.content}
              </EnhancedBubble>
            </EnhancedMessage>
          ))}
        </div>

        <InfoBox enhanced>
          <strong>设计特点：</strong>
          <FeatureList>
            {enhancedFeatures.map((feature, idx) => (
              <FeatureItem key={idx} enhanced>{feature}</FeatureItem>
            ))}
          </FeatureList>
        </InfoBox>
      </EnhancedCard>
    </EnhancedContainer>
  );

  const renderPlain = () => (
    <PlainContainer>
      <PlainCard>
        <PlainHeader>
          <Title>
            <MessageSquare size={24} />
            情感聊天机器人
          </Title>
          <Subtitle>温暖陪伴，理解倾听</Subtitle>
        </PlainHeader>

        <SectionTitle>
          <Layers size={24} />
          无特效版本（传统风格）
        </SectionTitle>

        <div>
          {sampleMessages.map((msg, idx) => (
            <PlainMessage key={idx} isUser={msg.role === 'user'}>
              <PlainAvatar isUser={msg.role === 'user'}>
                {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
              </PlainAvatar>
              <PlainBubble isUser={msg.role === 'user'}>
                {msg.content}
              </PlainBubble>
            </PlainMessage>
          ))}
        </div>

        <InfoBox>
          <strong>设计特点：</strong>
          <FeatureList>
            {plainFeatures.map((feature, idx) => (
              <FeatureItem key={idx}>{feature}</FeatureItem>
            ))}
          </FeatureList>
        </InfoBox>
      </PlainCard>
    </PlainContainer>
  );

  const renderComparison = () => (
    <EnhancedContainer>
      <ComparisonContainer>
        <ToggleContainer>
          <ToggleButton
            active={viewMode === 'comparison'}
            onClick={() => setViewMode('comparison')}
          >
            对比模式
          </ToggleButton>
          <ToggleButton
            active={viewMode === 'enhanced'}
            onClick={() => setViewMode('enhanced')}
          >
            特效版
          </ToggleButton>
          <ToggleButton
            active={viewMode === 'plain'}
            onClick={() => setViewMode('plain')}
          >
            传统版
          </ToggleButton>
        </ToggleContainer>

        <div style={{ textAlign: 'center', marginBottom: '40px', zIndex: 1, position: 'relative' }}>
          <Title enhanced style={{ fontSize: '2.5rem', marginBottom: '12px' }}>
            <Palette size={32} />
            样式对比演示
          </Title>
          <Subtitle enhanced style={{ fontSize: '1.2rem' }}>
            体验 Styled Components + 渐变色 + 毛玻璃效果带来的温暖氛围
          </Subtitle>
        </div>

        <ComparisonRow>
          {/* 有特效版本 */}
          <EnhancedCard
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5 }}
          >
            <EnhancedHeader>
              <Title enhanced style={{ fontSize: '1.3rem' }}>
                <Heart size={20} />
                有特效版本
              </Title>
              <Subtitle enhanced style={{ fontSize: '0.9rem' }}>
                渐变色 + 毛玻璃效果
              </Subtitle>
            </EnhancedHeader>

            <div>
              {sampleMessages.slice(0, 2).map((msg, idx) => (
                <EnhancedMessage key={idx} isUser={msg.role === 'user'}>
                  <EnhancedAvatar isUser={msg.role === 'user'}>
                    {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                  </EnhancedAvatar>
                  <EnhancedBubble isUser={msg.role === 'user'}>
                    {msg.content}
                  </EnhancedBubble>
                </EnhancedMessage>
              ))}
            </div>

            <InfoBox enhanced style={{ fontSize: '0.9rem' }}>
              <strong>✨ 设计亮点：</strong>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                <li>动态渐变背景</li>
                <li>毛玻璃模糊效果</li>
                <li>柔和阴影和光晕</li>
                <li>流畅动画过渡</li>
              </ul>
            </InfoBox>
          </EnhancedCard>

          {/* 无特效版本 */}
          <PlainCard>
            <PlainHeader>
              <Title style={{ fontSize: '1.3rem' }}>
                <Layers size={20} />
                无特效版本
              </Title>
              <Subtitle style={{ fontSize: '0.9rem' }}>
                传统风格
              </Subtitle>
            </PlainHeader>

            <div>
              {sampleMessages.slice(0, 2).map((msg, idx) => (
                <PlainMessage key={idx} isUser={msg.role === 'user'}>
                  <PlainAvatar isUser={msg.role === 'user'}>
                    {msg.role === 'user' ? <User size={18} /> : <Bot size={18} />}
                  </PlainAvatar>
                  <PlainBubble isUser={msg.role === 'user'}>
                    {msg.content}
                  </PlainBubble>
                </PlainMessage>
              ))}
            </div>

            <InfoBox style={{ fontSize: '0.9rem' }}>
              <strong>📦 设计特点：</strong>
              <ul style={{ marginTop: '8px', paddingLeft: '20px' }}>
                <li>纯色背景</li>
                <li>实心卡片</li>
                <li>标准边框</li>
                <li>简洁布局</li>
              </ul>
            </InfoBox>
          </PlainCard>
        </ComparisonRow>

        <EnhancedCard
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          style={{ marginTop: '20px' }}
        >
          <SectionTitle enhanced style={{ fontSize: '1.2rem', marginBottom: '16px' }}>
            <Palette size={20} />
            技术实现对比
          </SectionTitle>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div>
              <h4 style={{ color: 'rgba(255, 255, 255, 0.95)', marginBottom: '12px' }}>
                ✨ 有特效版本
              </h4>
              <pre style={{ 
                background: 'rgba(0, 0, 0, 0.2)', 
                padding: '16px', 
                borderRadius: '8px',
                color: 'rgba(255, 255, 255, 0.9)',
                fontSize: '0.85rem',
                overflow: 'auto'
              }}>
{`background: linear-gradient(
  135deg, 
  #667eea 0%, 
  #764ba2 100%
);

background: rgba(255, 255, 255, 0.95);
backdrop-filter: blur(20px);
box-shadow: 
  0 20px 60px rgba(0,0,0,0.3),
  0 0 100px rgba(102,126,234,0.2);`}
              </pre>
            </div>
            
            <div>
              <h4 style={{ color: '#666', marginBottom: '12px' }}>
                📦 无特效版本
              </h4>
              <pre style={{ 
                background: '#f8f9fa', 
                padding: '16px', 
                borderRadius: '8px',
                color: '#333',
                fontSize: '0.85rem',
                overflow: 'auto'
              }}>
{`background: #f5f5f5;

background: #ffffff;
border: 1px solid #e0e0e0;
box-shadow: 
  0 2px 8px rgba(0,0,0,0.1);`}
              </pre>
            </div>
          </div>
        </EnhancedCard>
      </ComparisonContainer>
    </EnhancedContainer>
  );

  if (viewMode === 'enhanced') {
    return (
      <>
        <ToggleContainer>
          <ToggleButton
            active={viewMode === 'comparison'}
            onClick={() => setViewMode('comparison')}
          >
            对比模式
          </ToggleButton>
          <ToggleButton
            active={viewMode === 'enhanced'}
            onClick={() => setViewMode('enhanced')}
          >
            特效版
          </ToggleButton>
          <ToggleButton
            active={viewMode === 'plain'}
            onClick={() => setViewMode('plain')}
          >
            传统版
          </ToggleButton>
        </ToggleContainer>
        {renderEnhanced()}
      </>
    );
  }

  if (viewMode === 'plain') {
    return (
      <>
        <ToggleContainer>
          <ToggleButton
            active={viewMode === 'comparison'}
            onClick={() => setViewMode('comparison')}
          >
            对比模式
          </ToggleButton>
          <ToggleButton
            active={viewMode === 'enhanced'}
            onClick={() => setViewMode('enhanced')}
          >
            特效版
          </ToggleButton>
          <ToggleButton
            active={viewMode === 'plain'}
            onClick={() => setViewMode('plain')}
          >
            传统版
          </ToggleButton>
        </ToggleContainer>
        {renderPlain()}
      </>
    );
  }

  return renderComparison();
}

export default StyleComparison;

