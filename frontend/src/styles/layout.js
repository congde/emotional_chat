import styled from 'styled-components';
import { motion } from 'framer-motion';

export const AppContainer = styled.div`
  min-height: 100vh;
  background: var(--bg-app);
  display: flex;
  color: var(--text-primary);
  transition: background 0.3s ease;
`;

export const Sidebar = styled(motion.div)`
  width: 248px;
  flex: 0 0 248px;
  background: var(--bg-subtle);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border-default);
  height: 100vh;
  position: sticky;
  top: 0;
  transition: background 0.3s ease, border-color 0.3s ease;
  
  @media (max-width: 840px) {
    display: none;
  }
`;

export const ChatContainer = styled(motion.div)`
  flex: 1;
  min-width: 0;
  background: var(--bg-panel);
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  transition: background 0.3s ease;

  @media (max-width: 840px) {
    padding-top: 52px;
  }

`;

export const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 40px 32px 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  transition: background 0.3s ease;
  
  @media (max-width: 768px) {
    padding: 20px 16px;
  }
`;

export const InputContainer = styled.div`
  padding: 12px 32px 24px;
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

