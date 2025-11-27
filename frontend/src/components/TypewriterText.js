import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

const TypewriterContainer = styled.div`
  display: inline-block;
`;

const TypewriterText = styled.span`
  display: inline-block;
  white-space: pre-wrap;
  word-wrap: break-word;
`;

const Cursor = styled.span`
  display: inline-block;
  width: 2px;
  height: 1.2em;
  background-color: ${props => props.color || '#333'};
  margin-left: 2px;
  animation: blink 1s infinite;
  
  @keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0; }
  }
`;

const TypewriterComponent = ({ 
  text, 
  speed = 30, 
  showCursor = true, 
  cursorColor = '#333',
  onComplete = () => {},
  isUser = false 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // 根据文本长度动态调整速度
  const getDynamicSpeed = (char, index) => {
    // 标点符号后稍作停顿
    if (['。', '！', '？', '.', '!', '?'].includes(char)) {
      return speed * 3;
    }
    // 逗号后短暂停顿
    if (['，', ',', ';', '；'].includes(char)) {
      return speed * 1.5;
    }
    // 空格稍快
    if (char === ' ') {
      return speed * 0.5;
    }
    // 中文字符稍慢
    if (/[\u4e00-\u9fa5]/.test(char)) {
      return speed * 1.2;
    }
    return speed;
  };

  useEffect(() => {
    if (currentIndex < text.length && !isPaused) {
      const currentChar = text[currentIndex];
      const dynamicSpeed = getDynamicSpeed(currentChar, currentIndex);
      
      const timer = setTimeout(() => {
        setDisplayedText(prev => prev + currentChar);
        setCurrentIndex(prev => prev + 1);
      }, dynamicSpeed);

      return () => clearTimeout(timer);
    } else if (currentIndex >= text.length && !isComplete) {
      setIsComplete(true);
      onComplete();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentIndex, text, speed, isComplete, onComplete, isPaused]);

  // 添加点击暂停/恢复功能
  const handleClick = () => {
    if (!isComplete) {
      setIsPaused(!isPaused);
    }
  };

  // 重置效果当文本改变时
  useEffect(() => {
    setDisplayedText('');
    setCurrentIndex(0);
    setIsComplete(false);
  }, [text]);

  return (
    <TypewriterContainer onClick={handleClick} style={{ cursor: !isComplete ? 'pointer' : 'default' }}>
      <TypewriterText>{displayedText}</TypewriterText>
      {showCursor && !isComplete && (
        <Cursor color={cursorColor} />
      )}
      {isPaused && !isComplete && (
        <span style={{ color: '#666', fontSize: '0.8em', marginLeft: '4px' }}>⏸️</span>
      )}
    </TypewriterContainer>
  );
};

export default TypewriterComponent;
