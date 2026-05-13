import styled from 'styled-components';
import { motion } from 'framer-motion';

export const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 15, 26, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

export const ModalContent = styled(motion.div)`
  background: #ffffff;
  border-radius: 20px;
  padding: 30px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(0, 0, 0, 0.06);
  
  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.06);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  }
`;

export const ModalHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  
  h3 {
    margin: 0;
    color: #1a1a2e;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.3px;
  }

  body[data-theme='dark'] & h3 {
    color: #f1f5f9;
  }
`;

export const CloseButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  color: #94a3b8;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.04);
    color: #334155;
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
  border-radius: 12px;
  border: 1.5px solid ${props => props.$active ? '#6366f1' : 'rgba(0, 0, 0, 0.08)'};
  background: ${props => props.$active ? 'rgba(99, 102, 241, 0.08)' : '#ffffff'};
  color: ${props => props.$active ? '#6366f1' : '#64748b'};
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  
  &:hover {
    border-color: rgba(99, 102, 241, 0.3);
    background: rgba(99, 102, 241, 0.04);
  }
  
  body[data-theme='dark'] & {
    border-color: ${props => props.$active ? '#818cf8' : 'rgba(255, 255, 255, 0.08)'};
    background: ${props => props.$active ? 'rgba(99, 102, 241, 0.15)' : '#1e293b'};
    color: ${props => props.$active ? '#818cf8' : '#94a3b8'};
  }
`;

export const RatingContainer = styled.div`
  margin-bottom: 20px;
  
  label {
    display: block;
    margin-bottom: 10px;
    color: #334155;
    font-weight: 600;
  }

  body[data-theme='dark'] & label {
    color: #e2e8f0;
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
  color: ${props => props.$active ? '#fbbf24' : '#e2e8f0'};
  transition: all 0.2s;
  padding: 0;
  
  &:hover {
    transform: scale(1.1);
  }
  
  body[data-theme='dark'] & {
    color: ${props => props.$active ? '#fbbf24' : '#334155'};
  }
`;

export const TextArea = styled.textarea`
  width: 100%;
  min-height: 100px;
  padding: 14px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 14px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
  color: #334155;
  background: #ffffff;
  
  &:focus {
    outline: none;
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
  }
  
  body[data-theme='dark'] & {
    background: #0f172a;
    border-color: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
    
    &:focus {
      border-color: rgba(99, 102, 241, 0.5);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    }
  }
`;

export const SubmitButton = styled(motion.button)`
  width: 100%;
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  color: white;
  border: none;
  padding: 13px;
  border-radius: 14px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  margin-top: 20px;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.25);
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.35);
    transform: translateY(-1px);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

