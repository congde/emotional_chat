import React, { useState, useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { X, Search, Brain, Heart, Calendar, BarChart3, Music, Shield, Zap, Plus, Upload, Trash2 } from 'lucide-react';
import styled from 'styled-components';
import ChatAPI from '../services/ChatAPI';

// Styled Components
const Overlay = styled(motion.div)`
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

const Panel = styled(motion.div)`
  background: #ffffff;
  border-radius: 20px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(0, 0, 0, 0.06);
  overflow: hidden;

  body[data-theme='dark'] & {
    background: #1e293b;
    border-color: rgba(255, 255, 255, 0.06);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
  }
`;

const PanelHeader = styled.div`
  padding: 20px 24px 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;

  body[data-theme='dark'] & {
    border-bottom-color: rgba(255, 255, 255, 0.06);
  }
`;

const PanelTitle = styled.h3`
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
  letter-spacing: -0.3px;

  body[data-theme='dark'] & {
    color: #f1f5f9;
  }
`;

const CloseBtn = styled.button`
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 6px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;

  &:hover {
    background: rgba(0, 0, 0, 0.04);
    color: #334155;
  }

  body[data-theme='dark'] &:hover {
    background: rgba(255, 255, 255, 0.06);
    color: #e2e8f0;
  }
`;

const SearchBox = styled.div`
  padding: 12px 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);

  body[data-theme='dark'] & {
    border-bottom-color: rgba(255, 255, 255, 0.04);
  }
`;

const SearchInput = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f8f9fb;
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.06);
  transition: all 0.2s;

  &:focus-within {
    border-color: rgba(99, 102, 241, 0.4);
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
  }

  body[data-theme='dark'] & {
    background: #0f172a;
    border-color: rgba(255, 255, 255, 0.06);

    &:focus-within {
      border-color: rgba(99, 102, 241, 0.5);
      background: #1e293b;
    }
  }

  input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 14px;
    color: #334155;
    background: transparent;
    font-family: inherit;

    &::placeholder {
      color: #cbd5e1;
    }

    body[data-theme='dark'] & {
      color: #e2e8f0;

      &::placeholder {
        color: #475569;
      }
    }
  }

  svg {
    color: #94a3b8;
    flex-shrink: 0;
  }
`;

const CategoryTabs = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 24px;
  overflow-x: auto;
  border-bottom: 1px solid rgba(0, 0, 0, 0.04);

  &::-webkit-scrollbar {
    display: none;
  }

  body[data-theme='dark'] & {
    border-bottom-color: rgba(255, 255, 255, 0.04);
  }
`;

const CategoryTab = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  min-width: 56px;
  height: 32px;
  margin: 0;
  padding: 0 14px;
  border-radius: 20px;
  border: 1px solid ${props => props.$active ? 'rgba(99, 102, 241, 0.3)' : 'rgba(0, 0, 0, 0.06)'};
  background: ${props => props.$active ? 'rgba(99, 102, 241, 0.08)' : 'transparent'};
  color: ${props => props.$active ? '#6366f1' : '#64748b'};
  appearance: none;
  box-sizing: border-box;
  font-family: inherit;
  font-size: 13px;
  font-weight: 500;
  line-height: 1;
  text-align: center;
  vertical-align: middle;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;

  &:hover {
    border-color: rgba(99, 102, 241, 0.2);
    color: #6366f1;
  }

  body[data-theme='dark'] & {
    border-color: ${props => props.$active ? 'rgba(99, 102, 241, 0.4)' : 'rgba(255, 255, 255, 0.06)'};
    background: ${props => props.$active ? 'rgba(99, 102, 241, 0.15)' : 'transparent'};
    color: ${props => props.$active ? '#818cf8' : '#94a3b8'};
  }
`;

const SkillsList = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const SkillCard = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 14px;
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: all 0.2s ease;

  &:hover {
    border-color: rgba(99, 102, 241, 0.2);
    box-shadow: 0 2px 12px rgba(99, 102, 241, 0.08);
    transform: translateY(-1px);
  }

  body[data-theme='dark'] & {
    background: #0f172a;
    border-color: rgba(255, 255, 255, 0.06);

    &:hover {
      border-color: rgba(99, 102, 241, 0.3);
      box-shadow: 0 2px 12px rgba(99, 102, 241, 0.15);
    }
  }
`;

const SkillIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: ${props => props.$bg || 'rgba(99, 102, 241, 0.08)'};
  color: ${props => props.$color || '#6366f1'};
`;

const SkillInfo = styled.div`
  flex: 1;
  min-width: 0;
`;

const SkillName = styled.div`
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 3px;

  body[data-theme='dark'] & {
    color: #e2e8f0;
  }
`;

const SkillDesc = styled.div`
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  body[data-theme='dark'] & {
    color: #64748b;
  }
`;

const SkillBadge = styled.span`
  padding: 3px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 500;
  background: rgba(99, 102, 241, 0.06);
  color: #6366f1;
  white-space: nowrap;

  body[data-theme='dark'] & {
    background: rgba(99, 102, 241, 0.12);
    color: #818cf8;
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #94a3b8;
  text-align: center;

  svg {
    margin-bottom: 12px;
    opacity: 0.5;
  }
`;

const ImportBtn = styled.button`
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.3);
  background: rgba(99, 102, 241, 0.06);
  color: #6366f1;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: rgba(99, 102, 241, 0.12);
    border-color: rgba(99, 102, 241, 0.5);
  }

  body[data-theme='dark'] & {
    background: rgba(99, 102, 241, 0.12);
    border-color: rgba(99, 102, 241, 0.3);
    color: #818cf8;

    &:hover {
      background: rgba(99, 102, 241, 0.2);
    }
  }
`;

const ImportBody = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ImportSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const ImportSectionTitle = styled.div`
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.5px;

  body[data-theme='dark'] & {
    color: #94a3b8;
  }
`;

const DropZone = styled.div`
  border: 2px dashed ${props => props.$dragOver ? 'rgba(99, 102, 241, 0.6)' : 'rgba(0, 0, 0, 0.1)'};
  border-radius: 14px;
  padding: 28px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
  background: ${props => props.$dragOver ? 'rgba(99, 102, 241, 0.04)' : 'transparent'};

  &:hover {
    border-color: rgba(99, 102, 241, 0.4);
    background: rgba(99, 102, 241, 0.02);
  }

  body[data-theme='dark'] & {
    border-color: ${props => props.$dragOver ? 'rgba(99, 102, 241, 0.6)' : 'rgba(255, 255, 255, 0.1)'};
    background: ${props => props.$dragOver ? 'rgba(99, 102, 241, 0.08)' : 'transparent'};
  }
`;

const DropZoneText = styled.span`
  font-size: 13px;
  color: #94a3b8;
  text-align: center;
  line-height: 1.5;
`;

const FormField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const FormLabel = styled.label`
  font-size: 12px;
  font-weight: 500;
  color: #64748b;

  body[data-theme='dark'] & {
    color: #94a3b8;
  }
`;

const FormInput = styled.input`
  padding: 9px 12px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #f8f9fb;
  font-size: 14px;
  color: #334155;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;

  &:focus {
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
  }

  body[data-theme='dark'] & {
    background: #0f172a;
    border-color: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
  }
`;

const FormSelect = styled.select`
  padding: 9px 12px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #f8f9fb;
  font-size: 14px;
  color: #334155;
  font-family: inherit;
  outline: none;
  transition: all 0.2s;
  cursor: pointer;

  &:focus {
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
  }

  body[data-theme='dark'] & {
    background: #0f172a;
    border-color: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
  }
`;

const FormTextarea = styled.textarea`
  padding: 9px 12px;
  border-radius: 10px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: #f8f9fb;
  font-size: 14px;
  color: #334155;
  font-family: inherit;
  outline: none;
  resize: vertical;
  min-height: 60px;
  transition: all 0.2s;

  &:focus {
    border-color: rgba(99, 102, 241, 0.4);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.08);
  }

  body[data-theme='dark'] & {
    background: #0f172a;
    border-color: rgba(255, 255, 255, 0.08);
    color: #e2e8f0;
  }
`;

const SubmitBtn = styled.button`
  padding: 10px 20px;
  border-radius: 12px;
  border: none;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const ImportedBadge = styled.span`
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 600;
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  margin-left: 6px;
`;

const DeleteBtn = styled.button`
  padding: 4px;
  border-radius: 6px;
  border: none;
  background: none;
  color: #94a3b8;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
  flex-shrink: 0;

  &:hover {
    background: rgba(239, 68, 68, 0.08);
    color: #ef4444;
  }
`;

const ImportResult = styled.div`
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13px;
  background: ${props => props.$error ? 'rgba(239, 68, 68, 0.08)' : 'rgba(16, 185, 129, 0.08)'};
  color: ${props => props.$error ? '#ef4444' : '#10b981'};
  border: 1px solid ${props => props.$error ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)'};
`;

const Divider = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  color: #cbd5e1;
  font-size: 12px;

  &::before, &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(0, 0, 0, 0.06);

    body[data-theme='dark'] & {
      background: rgba(255, 255, 255, 0.06);
    }
  }
`;

// Category config
const categoryConfig = {
  all: { label: '全部', icon: Zap },
  emotion: { label: '情绪', icon: Heart },
  memory: { label: '记忆', icon: Brain },
  resource: { label: '资源', icon: Music },
  assessment: { label: '评估', icon: BarChart3 },
  scheduler: { label: '日程', icon: Calendar },
};

const skillIconMap = {
  memory: { icon: Brain, bg: 'rgba(99, 102, 241, 0.08)', color: '#6366f1' },
  emotion: { icon: Heart, bg: 'rgba(239, 68, 68, 0.08)', color: '#ef4444' },
  resource: { icon: Music, bg: 'rgba(16, 185, 129, 0.08)', color: '#10b981' },
  assessment: { icon: Shield, bg: 'rgba(245, 158, 11, 0.08)', color: '#f59e0b' },
  scheduler: { icon: Calendar, bg: 'rgba(139, 92, 246, 0.08)', color: '#8b5cf6' },
};

const skillDisplayNames = {
  search_memory: '搜索记忆',
  get_emotion_log: '情绪日志',
  recommend_meditation: '冥想推荐',
  psychological_assessment: '心理评估',
  set_reminder: '设置提醒',
  get_user_mood_trend: '情绪趋势',
  recommend_resource: '资源推荐',
  play_meditation_audio: '冥想音频',
  set_daily_reminder: '每日提醒',
  search_mental_health_resources: '心理健康资源',
  send_follow_up_message: '回访关怀',
  check_calendar: '查看日历',
};

const IMPORTED_SKILLS_KEY = 'xinyu_imported_skills';

const loadImportedSkills = () => {
  try {
    const saved = localStorage.getItem(IMPORTED_SKILLS_KEY);
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
};

const saveImportedSkills = (skills) => {
  localStorage.setItem(IMPORTED_SKILLS_KEY, JSON.stringify(skills));
};

const SkillsPanel = ({ isOpen, onClose, onSelectSkill, initialCategory = 'all' }) => {
  const [skills, setSkills] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [loading, setLoading] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', category: 'emotion' });
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      setActiveCategory(initialCategory);
      loadSkills();
    }
  }, [isOpen, initialCategory]);

  const loadSkills = async () => {
    setLoading(true);
    try {
      const data = await ChatAPI.getAvailableSkills();
      const toolsList = data.tools || data || [];
      const parsedSkills = Array.isArray(toolsList) ? toolsList : [];
      const builtinSkills = parsedSkills.length > 0 ? parsedSkills : getDefaultSkills();
      const importedSkills = loadImportedSkills();
      setSkills([...builtinSkills, ...importedSkills]);
    } catch (err) {
      console.error('Failed to load skills:', err);
      const importedSkills = loadImportedSkills();
      setSkills([...getDefaultSkills(), ...importedSkills]);
    } finally {
      setLoading(false);
    }
  };

  const getDefaultSkills = () => [
    { name: 'search_memory', category: 'memory', description: '搜索历史记忆和对话' },
    { name: 'get_emotion_log', category: 'emotion', description: '查看情绪变化趋势' },
    { name: 'get_user_mood_trend', category: 'emotion', description: '分析近期情绪模式和变化' },
    { name: 'recommend_meditation', category: 'resource', description: '推荐冥想和放松资源' },
    { name: 'play_meditation_audio', category: 'resource', description: '播放冥想引导音频' },
    { name: 'psychological_assessment', category: 'assessment', description: '心理状态快速评估' },
    { name: 'set_reminder', category: 'scheduler', description: '设置提醒和日程安排' },
    { name: 'check_calendar', category: 'scheduler', description: '查看近期日程安排' },
    { name: 'search_mental_health_resources', category: 'resource', description: '搜索心理健康相关资源' },
    { name: 'send_follow_up_message', category: 'emotion', description: '设置主动回访关怀' },
  ];

  const filteredSkills = skills.filter(skill => {
    const matchesSearch = !searchQuery ||
      (skill.name && skill.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (skill.description && skill.description.includes(searchQuery)) ||
      (skillDisplayNames[skill.name] && skillDisplayNames[skill.name].includes(searchQuery));

    const matchesCategory = activeCategory === 'all' || skill.category === activeCategory;

    return matchesSearch && matchesCategory;
  });

  const getSkillIcon = (category) => {
    const config = skillIconMap[category] || skillIconMap.memory;
    return config;
  };

  const handleSelectSkill = (skill) => {
    if (onSelectSkill) {
      onSelectSkill(skill);
    }
    onClose();
  };

  // --- Import handlers ---
  const handleFileImport = (file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = JSON.parse(e.target.result);
        const newSkills = Array.isArray(content) ? content : (content.skills || content.tools || [content]);
        const validSkills = newSkills.filter(s => s.name && s.description).map(s => ({
          name: String(s.name).replace(/[^a-zA-Z0-9_]/g, '_').substring(0, 50),
          description: String(s.description).substring(0, 200),
          category: categoryConfig[s.category] ? s.category : 'emotion',
          imported: true,
        }));
        if (validSkills.length === 0) {
          setImportResult({ error: true, message: 'JSON 中未找到有效技能（需要 name 和 description 字段）' });
          return;
        }
        const imported = loadImportedSkills();
        const existingNames = new Set([...imported.map(s => s.name), ...getDefaultSkills().map(s => s.name)]);
        const deduplicated = validSkills.filter(s => !existingNames.has(s.name));
        if (deduplicated.length === 0) {
          setImportResult({ error: true, message: '所有技能已存在，无需重复导入' });
          return;
        }
        const updated = [...imported, ...deduplicated];
        saveImportedSkills(updated);
        setSkills(prev => [...prev, ...deduplicated]);
        setImportResult({ error: false, message: `成功导入 ${deduplicated.length} 个技能` });
        setTimeout(() => setImportResult(null), 3000);
      } catch (err) {
        setImportResult({ error: true, message: '文件解析失败，请确认是有效的 JSON 格式' });
      }
    };
    reader.readAsText(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && (file.type === 'application/json' || file.name.endsWith('.json'))) {
      handleFileImport(file);
    } else {
      setImportResult({ error: true, message: '仅支持 .json 文件' });
    }
  };

  const handleManualAdd = () => {
    if (!formData.name.trim() || !formData.description.trim()) return;
    const skillName = formData.name.trim().replace(/[^a-zA-Z0-9_\u4e00-\u9fff]/g, '_').substring(0, 50);
    const imported = loadImportedSkills();
    const allNames = new Set([...imported.map(s => s.name), ...getDefaultSkills().map(s => s.name)]);
    if (allNames.has(skillName)) {
      setImportResult({ error: true, message: `技能 "${skillName}" 已存在` });
      return;
    }
    const newSkill = {
      name: skillName,
      description: formData.description.trim().substring(0, 200),
      category: formData.category,
      imported: true,
    };
    const updated = [...imported, newSkill];
    saveImportedSkills(updated);
    setSkills(prev => [...prev, newSkill]);
    setFormData({ name: '', description: '', category: 'emotion' });
    setImportResult({ error: false, message: `技能 "${skillName}" 已添加` });
    setTimeout(() => setImportResult(null), 3000);
  };

  const handleDeleteImported = (e, skillName) => {
    e.stopPropagation();
    const imported = loadImportedSkills().filter(s => s.name !== skillName);
    saveImportedSkills(imported);
    setSkills(prev => prev.filter(s => s.name !== skillName || !s.imported));
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <Overlay
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <Panel
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.2 }}
          onClick={(e) => e.stopPropagation()}
        >
          <PanelHeader>
            <PanelTitle>{showImport ? '导入技能' : '选择技能'}</PanelTitle>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              {!showImport && (
                <ImportBtn onClick={() => { setShowImport(true); setImportResult(null); }}>
                  <Plus size={14} />
                  导入
                </ImportBtn>
              )}
              <CloseBtn onClick={() => { showImport ? setShowImport(false) : onClose(); }}>
                <X size={20} />
              </CloseBtn>
            </div>
          </PanelHeader>

          {showImport ? (
            <ImportBody>
              <ImportSection>
                <ImportSectionTitle>从文件导入</ImportSectionTitle>
                <DropZone
                  $dragOver={dragOver}
                  onClick={() => fileInputRef.current?.click()}
                  onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleDrop}
                >
                  <Upload size={28} color="#94a3b8" />
                  <DropZoneText>
                    拖拽 JSON 文件到此处，或点击选择文件<br/>
                    <span style={{ fontSize: '11px', color: '#cbd5e1' }}>
                      格式：{'[{"name": "...", "description": "...", "category": "emotion|memory|resource|assessment|scheduler"}]'}
                    </span>
                  </DropZoneText>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".json,application/json"
                    style={{ display: 'none' }}
                    onChange={(e) => handleFileImport(e.target.files[0])}
                  />
                </DropZone>
              </ImportSection>

              <Divider>或</Divider>

              <ImportSection>
                <ImportSectionTitle>手动添加技能</ImportSectionTitle>
                <FormField>
                  <FormLabel>技能名称</FormLabel>
                  <FormInput
                    placeholder="如：daily_journal"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  />
                </FormField>
                <FormField>
                  <FormLabel>描述</FormLabel>
                  <FormTextarea
                    placeholder="技能的功能描述..."
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  />
                </FormField>
                <FormField>
                  <FormLabel>分类</FormLabel>
                  <FormSelect
                    value={formData.category}
                    onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                  >
                    {Object.entries(categoryConfig).filter(([k]) => k !== 'all').map(([key, config]) => (
                      <option key={key} value={key}>{config.label}</option>
                    ))}
                  </FormSelect>
                </FormField>
                <SubmitBtn
                  disabled={!formData.name.trim() || !formData.description.trim()}
                  onClick={handleManualAdd}
                >
                  添加技能
                </SubmitBtn>
              </ImportSection>

              {importResult && (
                <ImportResult $error={importResult.error}>
                  {importResult.message}
                </ImportResult>
              )}
            </ImportBody>
          ) : (
            <>
              <SearchBox>
                <SearchInput>
                  <Search size={16} />
                  <input
                    type="text"
                    placeholder="搜索技能..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    autoFocus
                  />
                </SearchInput>
              </SearchBox>

              <CategoryTabs>
                {Object.entries(categoryConfig).map(([key, config]) => (
                  <CategoryTab
                    key={key}
                    $active={activeCategory === key}
                    onClick={() => setActiveCategory(key)}
                  >
                    {config.label}
                  </CategoryTab>
                ))}
              </CategoryTabs>

              <SkillsList>
                {loading ? (
                  <EmptyState>
                    <Zap size={32} />
                    <span>加载技能中...</span>
                  </EmptyState>
                ) : filteredSkills.length === 0 ? (
                  <EmptyState>
                    <Search size={32} />
                    <span>未找到匹配的技能</span>
                  </EmptyState>
                ) : (
                  filteredSkills.map((skill, index) => {
                    const iconConfig = getSkillIcon(skill.category);
                    const IconComponent = iconConfig.icon;
                    return (
                      <SkillCard
                        key={skill.name || index}
                        onClick={() => handleSelectSkill(skill)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                handleSelectSkill(skill);
                              }
                            }}
                            role="button"
                            tabIndex={0}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.03 }}
                      >
                        <SkillIcon $bg={iconConfig.bg} $color={iconConfig.color}>
                          <IconComponent size={20} />
                        </SkillIcon>
                        <SkillInfo>
                          <SkillName>
                            {skillDisplayNames[skill.name] || skill.name}
                            {skill.imported && <ImportedBadge>导入</ImportedBadge>}
                          </SkillName>
                          <SkillDesc>{skill.description || '智能工具'}</SkillDesc>
                        </SkillInfo>
                        {skill.imported ? (
                          <DeleteBtn onClick={(e) => handleDeleteImported(e, skill.name)} title="删除">
                            <Trash2 size={14} />
                          </DeleteBtn>
                        ) : (
                          <SkillBadge>{categoryConfig[skill.category]?.label || '工具'}</SkillBadge>
                        )}
                      </SkillCard>
                    );
                  })
                )}
              </SkillsList>
            </>
          )}
        </Panel>
      </Overlay>
    </AnimatePresence>
  );
};

export default SkillsPanel;
