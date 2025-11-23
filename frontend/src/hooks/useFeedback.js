import { useState } from 'react';
import ChatAPI from '../services/ChatAPI';

export const useFeedback = (sessionId, currentUserId, messages) => {
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState(null);
  const [feedbackType, setFeedbackType] = useState('');
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');

  const openFeedbackModal = (message) => {
    setFeedbackMessage(message);
    setShowFeedbackModal(true);
    setFeedbackType('');
    setFeedbackRating(0);
    setFeedbackComment('');
  };

  const closeFeedbackModal = () => {
    setShowFeedbackModal(false);
    setFeedbackMessage(null);
    setFeedbackType('');
    setFeedbackRating(0);
    setFeedbackComment('');
  };

  const submitFeedback = async () => {
    if (!feedbackType || feedbackRating === 0) {
      alert('请选择反馈类型和评分');
      return;
    }

    try {
      // 找到用户消息（与bot回复对应的前一条消息）
      const messageIndex = messages.findIndex(m => m.id === feedbackMessage.id);
      const userMessage = messageIndex > 0 ? messages[messageIndex - 1] : null;

      const feedbackData = {
        session_id: sessionId || 'unknown',
        user_id: currentUserId,
        message_id: feedbackMessage.id,
        feedback_type: feedbackType,
        rating: feedbackRating,
        comment: feedbackComment,
        user_message: userMessage?.content || '',
        bot_response: feedbackMessage.content
      };

      await ChatAPI.submitFeedback(feedbackData);
      alert('感谢您的反馈！');
      closeFeedbackModal();
    } catch (error) {
      console.error('提交反馈失败:', error);
      alert('提交反馈失败，请稍后重试');
    }
  };

  return {
    showFeedbackModal,
    feedbackMessage,
    feedbackType,
    feedbackRating,
    feedbackComment,
    openFeedbackModal,
    closeFeedbackModal,
    setFeedbackType,
    setFeedbackRating,
    setFeedbackComment,
    submitFeedback
  };
};

