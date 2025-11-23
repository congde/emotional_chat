import styled from 'styled-components';
import { motion } from 'framer-motion';

export const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  
  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

export const Sidebar = styled(motion.div)`
  width: 300px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  
  @media (max-width: 768px) {
    width: 100%;
    max-height: 40vh;
    border-right: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  }
`;

export const ChatContainer = styled(motion.div)`
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  backdrop-filter: blur(10px);
`;

export const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

export const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

export const InputRow = styled.div`
  display: flex;
  gap: 10px;
  align-items: center;
`;

