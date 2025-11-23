import styled from 'styled-components';
import { motion } from 'framer-motion';

export const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

export const ModalContent = styled(motion.div)`
  background: white;
  border-radius: 20px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
`;

export const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  
  h3 {
    margin: 0;
    color: #333;
    font-size: 1.3rem;
  }
`;

export const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #333;
  }
`;

export const FeedbackTypeButtons = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
`;

export const TypeButton = styled(motion.button)`
  padding: 10px 16px;
  border-radius: 10px;
  border: 2px solid ${props => props.active ? '#667eea' : '#ddd'};
  background: ${props => props.active ? 'rgba(102, 126, 234, 0.1)' : 'white'};
  color: ${props => props.active ? '#667eea' : '#666'};
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  
  &:hover {
    border-color: #667eea;
    background: rgba(102, 126, 234, 0.05);
  }
`;

export const RatingContainer = styled.div`
  margin-bottom: 20px;
  
  label {
    display: block;
    margin-bottom: 10px;
    color: #333;
    font-weight: 500;
  }
`;

export const RatingStars = styled.div`
  display: flex;
  gap: 8px;
`;

export const StarButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  font-size: 2rem;
  color: ${props => props.active ? '#ffd93d' : '#ddd'};
  transition: all 0.2s;
  padding: 0;
  
  &:hover {
    transform: scale(1.1);
  }
`;

export const TextArea = styled.textarea`
  width: 100%;
  min-height: 100px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

export const SubmitButton = styled(motion.button)`
  width: 100%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  padding: 12px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 20px;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

