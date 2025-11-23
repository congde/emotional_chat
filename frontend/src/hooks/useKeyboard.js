import { useEffect } from 'react';

export const useKeyboard = (startNewChat, sendMessage, inputRef, attachmentButtonRef, sendButtonRef) => {
  // Enter键发送消息
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Ctrl+N 新建对话快捷键
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.key === 'n') {
        e.preventDefault();
        startNewChat();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [startNewChat]);

  // 键盘导航支持（Tab键自定义导航）
  const handleTabNavigation = (e) => {
    if (e.key === 'Tab') {
      // 自定义Tab顺序
      const focusableElements = [
        inputRef.current,
        attachmentButtonRef.current,
        sendButtonRef.current
      ].filter(el => el && !el.disabled); // 过滤掉禁用和null的元素

      const currentIndex = focusableElements.indexOf(document.activeElement);
      const nextIndex = (currentIndex + 1) % focusableElements.length;

      e.preventDefault();
      focusableElements[nextIndex]?.focus();
    }
  };

  return {
    handleKeyPress,
    handleTabNavigation
  };
};

