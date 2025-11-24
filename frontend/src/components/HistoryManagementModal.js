import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Search, Trash2, RotateCcw } from 'lucide-react';
import ChatAPI from '../services/ChatAPI';
import { formatRelativeTime } from '../utils/formatters';
import {
  ModalOverlay,
  ModalContent,
  ModalHeader,
  CloseButton
} from '../styles/modal';
import styled from 'styled-components';

// 历史管理模态专用样式
const HistoryModalContent = styled(ModalContent)`
  max-width: 800px;
  width: 90%;
  max-height: 85vh;
  padding: 0;
  display: flex;
  flex-direction: column;
`;

const HistoryModalHeader = styled(ModalHeader)`
  padding: 24px 30px;
  border-bottom: 1px solid #eee;
  margin-bottom: 0;
  
  h3 {
    font-size: 1.4rem;
    font-weight: 600;
  }
`;

const SearchContainer = styled.div`
  padding: 20px 30px;
  border-bottom: 1px solid #eee;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 0.95rem;
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const SearchIcon = styled(Search)`
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
  pointer-events: none;
`;

const SearchWrapper = styled.div`
  position: relative;
  display: flex;
  align-items: center;
`;

const ClearSearchButton = styled.button`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #333;
  }
`;

const SessionsList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 0;
  min-height: 300px;
`;

const SessionTable = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background: #f8f9fa;
  position: sticky;
  top: 0;
  z-index: 10;
`;

const TableHeaderRow = styled.tr`
  border-bottom: 2px solid #eee;
`;

const TableHeaderCell = styled.th`
  padding: 16px 30px;
  text-align: left;
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
  
  &:first-child {
    width: 50px;
    text-align: center;
  }
  
  &:last-child {
    width: 100px;
    text-align: center;
  }
`;

const TableBody = styled.tbody``;

const TableRow = styled(motion.tr)`
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #f8f9fa;
  }
  
  ${props => props.selected && `
    background: rgba(102, 126, 234, 0.05);
  `}
`;

const TableCell = styled.td`
  padding: 16px 30px;
  color: #333;
  font-size: 0.95rem;
  
  &:first-child {
    text-align: center;
  }
  
  &:last-child {
    text-align: center;
  }
`;

const Checkbox = styled.input`
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #667eea;
`;

const SessionTitle = styled.div`
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
`;

const SessionTime = styled.div`
  font-size: 0.85rem;
  color: #999;
`;

const ActionButton = styled(motion.button)`
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(0, 0, 0, 0.05);
    color: #ff4757;
  }
`;

const Footer = styled.div`
  padding: 20px 30px;
  border-top: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f8f9fa;
`;

const SelectAllContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  
  label {
    font-size: 0.95rem;
    color: #333;
    cursor: pointer;
    user-select: none;
  }
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const FooterButton = styled(motion.button)`
  padding: 10px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  
  ${props => props.primary ? `
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    
    &:hover:not(:disabled) {
      box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  ` : `
    background: white;
    color: #666;
    border: 1px solid #ddd;
    
    &:hover {
      background: #f8f9fa;
      border-color: #ccc;
    }
  `}
`;

const EmptyState = styled.div`
  padding: 60px 30px;
  text-align: center;
  color: #999;
  
  div {
    font-size: 1.1rem;
    margin-bottom: 8px;
  }
`;

const LoadingState = styled.div`
  padding: 60px 30px;
  text-align: center;
  color: #999;
`;

const HistoryManagementModal = ({
  show,
  onClose,
  userId,
  onSessionSelect,
  onSessionsDeleted
}) => {
  const [sessions, setSessions] = useState([]);
  const [filteredSessions, setFilteredSessions] = useState([]);
  const [selectedSessions, setSelectedSessions] = useState(new Set());
  const [searchKeyword, setSearchKeyword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // 加载会话列表
  const loadSessions = useCallback(async (keyword = '') => {
    setIsLoading(true);
    try {
      let response;
      if (keyword.trim()) {
        response = await ChatAPI.searchUserSessions(userId, keyword);
      } else {
        response = await ChatAPI.getUserSessions(userId, 100);
      }
      const sessionsList = response.sessions || [];
      setSessions(sessionsList);
      setFilteredSessions(sessionsList);
    } catch (error) {
      console.error('加载会话列表失败:', error);
      setSessions([]);
      setFilteredSessions([]);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // 初始加载
  useEffect(() => {
    if (show) {
      loadSessions();
      setSearchKeyword('');
      setSelectedSessions(new Set());
    }
  }, [show, loadSessions]);

  // 搜索处理
  const handleSearch = useCallback(async (keyword) => {
    setSearchKeyword(keyword);
    if (keyword.trim()) {
      setIsLoading(true);
      try {
        const response = await ChatAPI.searchUserSessions(userId, keyword);
        const sessionsList = response.sessions || [];
        setFilteredSessions(sessionsList);
      } catch (error) {
        console.error('搜索会话失败:', error);
        setFilteredSessions([]);
      } finally {
        setIsLoading(false);
      }
    } else {
      setFilteredSessions(sessions);
    }
  }, [userId, sessions]);

  // 选择/取消选择会话
  const toggleSession = (sessionId) => {
    const newSelected = new Set(selectedSessions);
    if (newSelected.has(sessionId)) {
      newSelected.delete(sessionId);
    } else {
      newSelected.add(sessionId);
    }
    setSelectedSessions(newSelected);
  };

  // 全选/取消全选
  const toggleSelectAll = () => {
    if (selectedSessions.size === filteredSessions.length) {
      setSelectedSessions(new Set());
    } else {
      setSelectedSessions(new Set(filteredSessions.map(s => s.session_id)));
    }
  };

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedSessions.size === 0) return;
    
    if (!window.confirm(`确定要删除选中的 ${selectedSessions.size} 个对话吗？此操作无法撤销。`)) {
      return;
    }

    setIsDeleting(true);
    try {
      const sessionIds = Array.from(selectedSessions);
      await ChatAPI.deleteSessionsBatch(sessionIds);
      
      // 重新加载列表
      await loadSessions(searchKeyword);
      setSelectedSessions(new Set());
      
      // 通知父组件
      if (onSessionsDeleted) {
        onSessionsDeleted(sessionIds);
      }
    } catch (error) {
      console.error('批量删除失败:', error);
      alert('删除失败，请稍后重试');
    } finally {
      setIsDeleting(false);
    }
  };

  // 单个删除
  const handleSingleDelete = async (sessionId, e) => {
    e.stopPropagation();
    
    if (!window.confirm('确定要删除这个对话吗？此操作无法撤销。')) {
      return;
    }

    try {
      await ChatAPI.deleteSession(sessionId);
      
      // 重新加载列表
      await loadSessions(searchKeyword);
      
      // 从选中列表中移除
      const newSelected = new Set(selectedSessions);
      newSelected.delete(sessionId);
      setSelectedSessions(newSelected);
      
      // 通知父组件
      if (onSessionsDeleted) {
        onSessionsDeleted([sessionId]);
      }
    } catch (error) {
      console.error('删除会话失败:', error);
      alert('删除失败，请稍后重试');
    }
  };

  // 点击会话行
  const handleSessionClick = (sessionId) => {
    if (onSessionSelect) {
      onSessionSelect(sessionId);
      onClose();
    }
  };

  if (!show) return null;

  return (
    <AnimatePresence>
      <ModalOverlay
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <HistoryModalContent
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <HistoryModalHeader>
            <h3>管理对话记录 · 共{filteredSessions.length}条</h3>
            <CloseButton onClick={onClose}>
              <X size={20} />
            </CloseButton>
          </HistoryModalHeader>

          <SearchContainer>
            <SearchWrapper>
              <SearchIcon size={18} />
              <SearchInput
                type="text"
                placeholder="搜索历史记录"
                value={searchKeyword}
                onChange={(e) => handleSearch(e.target.value)}
              />
              {searchKeyword && (
                <ClearSearchButton
                  onClick={() => handleSearch('')}
                  title="清除搜索"
                >
                  <X size={16} />
                </ClearSearchButton>
              )}
            </SearchWrapper>
          </SearchContainer>

          <SessionsList>
            {isLoading ? (
              <LoadingState>
                <div>加载中...</div>
              </LoadingState>
            ) : filteredSessions.length === 0 ? (
              <EmptyState>
                <div>{searchKeyword ? '没有找到匹配的对话' : '还没有历史对话'}</div>
                <div style={{ fontSize: '0.9rem', marginTop: '8px' }}>
                  {searchKeyword ? '尝试使用其他关键词搜索' : '开始一段新的对话吧！'}
                </div>
              </EmptyState>
            ) : (
              <SessionTable>
                <TableHeader>
                  <TableHeaderRow>
                    <TableHeaderCell>
                      <Checkbox
                        type="checkbox"
                        checked={filteredSessions.length > 0 && selectedSessions.size === filteredSessions.length}
                        onChange={toggleSelectAll}
                      />
                    </TableHeaderCell>
                    <TableHeaderCell>对话名称</TableHeaderCell>
                    <TableHeaderCell>最近一次对话时间</TableHeaderCell>
                    <TableHeaderCell>操作</TableHeaderCell>
                  </TableHeaderRow>
                </TableHeader>
                <TableBody>
                  <AnimatePresence>
                    {filteredSessions.map((session) => (
                      <TableRow
                        key={session.session_id}
                        selected={selectedSessions.has(session.session_id)}
                        onClick={() => handleSessionClick(session.session_id)}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                      >
                        <TableCell onClick={(e) => e.stopPropagation()}>
                          <Checkbox
                            type="checkbox"
                            checked={selectedSessions.has(session.session_id)}
                            onChange={() => toggleSession(session.session_id)}
                          />
                        </TableCell>
                        <TableCell>
                          <SessionTitle>{session.title || '新对话'}</SessionTitle>
                          {session.preview && (
                            <div style={{ fontSize: '0.85rem', color: '#999', marginTop: '4px' }}>
                              {session.preview}
                            </div>
                          )}
                        </TableCell>
                        <TableCell>
                          <SessionTime>
                            {session.updated_at ? formatRelativeTime(session.updated_at) : '未知'}
                          </SessionTime>
                        </TableCell>
                        <TableCell onClick={(e) => e.stopPropagation()}>
                          <ActionButton
                            onClick={(e) => handleSingleDelete(session.session_id, e)}
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                            title="删除对话"
                          >
                            <Trash2 size={16} />
                          </ActionButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </AnimatePresence>
                </TableBody>
              </SessionTable>
            )}
          </SessionsList>

          <Footer>
            <SelectAllContainer>
              <Checkbox
                type="checkbox"
                checked={filteredSessions.length > 0 && selectedSessions.size === filteredSessions.length}
                onChange={toggleSelectAll}
                id="select-all"
              />
              <label htmlFor="select-all">全选</label>
            </SelectAllContainer>
            <ActionButtons>
              <FooterButton
                onClick={onClose}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                取消
              </FooterButton>
              <FooterButton
                primary
                onClick={handleBatchDelete}
                disabled={selectedSessions.size === 0 || isDeleting}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {isDeleting ? '删除中...' : `删除所选 (${selectedSessions.size})`}
              </FooterButton>
            </ActionButtons>
          </Footer>
        </HistoryModalContent>
      </ModalOverlay>
    </AnimatePresence>
  );
};

export default HistoryManagementModal;

