import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { X } from 'lucide-react';
import {
  ModalOverlay,
  ModalContent,
  ModalHeader,
  CloseButton,
  FeedbackTypeButtons,
  TypeButton,
  RatingContainer,
  RatingStars,
  StarButton,
  TextArea,
  SubmitButton
} from '../styles/modal';

const FeedbackModal = ({
  show,
  feedbackType,
  feedbackRating,
  feedbackComment,
  onClose,
  onTypeChange,
  onRatingChange,
  onCommentChange,
  onSubmit
}) => {
  if (!show) return null;

  return (
    <AnimatePresence>
      <ModalOverlay
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <ModalContent
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <ModalHeader>
            <h3>提交反馈</h3>
            <CloseButton onClick={onClose}>
              <X size={20} />
            </CloseButton>
          </ModalHeader>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '500' }}>
              反馈类型
            </label>
            <FeedbackTypeButtons>
              <TypeButton
                active={feedbackType === 'helpful'}
                onClick={() => onTypeChange('helpful')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                ✅ 有帮助
              </TypeButton>
              <TypeButton
                active={feedbackType === 'irrelevant'}
                onClick={() => onTypeChange('irrelevant')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                ❌ 答非所问
              </TypeButton>
              <TypeButton
                active={feedbackType === 'lack_empathy'}
                onClick={() => onTypeChange('lack_empathy')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                😐 缺乏共情
              </TypeButton>
              <TypeButton
                active={feedbackType === 'overstepping'}
                onClick={() => onTypeChange('overstepping')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                ⚠️ 越界建议
              </TypeButton>
              <TypeButton
                active={feedbackType === 'other'}
                onClick={() => onTypeChange('other')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                📝 其他
              </TypeButton>
            </FeedbackTypeButtons>
          </div>

          <RatingContainer>
            <label>评分</label>
            <RatingStars>
              {[1, 2, 3, 4, 5].map((star) => (
                <StarButton
                  key={star}
                  active={feedbackRating >= star}
                  onClick={() => onRatingChange(star)}
                >
                  {feedbackRating >= star ? '★' : '☆'}
                </StarButton>
              ))}
            </RatingStars>
          </RatingContainer>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '500' }}>
              详细说明（选填）
            </label>
            <TextArea
              value={feedbackComment}
              onChange={(e) => onCommentChange(e.target.value)}
              placeholder="请描述您的具体感受或建议..."
            />
          </div>

          <SubmitButton
            onClick={onSubmit}
            disabled={!feedbackType || feedbackRating === 0}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            提交反馈
          </SubmitButton>
        </ModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

export default FeedbackModal;

