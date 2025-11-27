import styled from 'styled-components';
import { motion } from 'framer-motion';

export const AppContainer = styled.div`
  min-height: 100vh;
  background: #f5f5f5;
  display: flex;
`;

export const Sidebar = styled(motion.div)`
  width: 240px;
  background: #fff;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e8e8e8;
  height: 100vh;
  position: sticky;
  top: 0;
  
  @media (max-width: 768px) {
    display: none;
  }
`;

export const ChatContainer = styled(motion.div)`
  flex: 1;
  background: #fff;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
`;

export const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px 60px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  
  @media (max-width: 768px) {
    padding: 20px;
  }
`;

export const InputContainer = styled.div`
  padding: 20px 60px 30px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #fff;
  
  @media (max-width: 768px) {
    padding: 16px;
  }
`;

export const InputRow = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

