import styled from 'styled-components';
import { motion } from 'framer-motion';

export const AppContainer = styled.div`
  min-height: 100vh;
  background: #f8f9fb;
  display: flex;
  transition: background 0.3s ease;

  body[data-theme='dark'] & {
    background: #0f0f1a;
  }
`;

export const Sidebar = styled(motion.div)`
  width: 280px;
  background: #ffffff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  height: 100vh;
  position: sticky;
  top: 0;
  transition: background 0.3s ease, border-color 0.3s ease;
  
  body[data-theme='dark'] & {
    background: #141422;
    border-right-color: rgba(255, 255, 255, 0.06);
  }
  
  @media (max-width: 768px) {
    display: none;
  }
`;

export const ChatContainer = styled(motion.div)`
  flex: 1;
  background: #f8f9fb;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  transition: background 0.3s ease;

  body[data-theme='dark'] & {
    background: #0f0f1a;
  }
`;

export const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 32px 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  transition: background 0.3s ease;
  
  body[data-theme='dark'] & {
    background: #0f0f1a;
  }
  
  @media (max-width: 768px) {
    padding: 20px 16px;
  }
`;

export const InputContainer = styled.div`
  padding: 16px 40px 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: transparent;
  
  @media (max-width: 768px) {
    padding: 12px 16px 20px;
  }
`;

export const InputRow = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

