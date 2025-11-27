import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  User, 
  Zap, 
  MessageCircle, 
  Settings, 
  Sparkles,
  Check,
  Bot
} from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 样式组件
const Overlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
`;

const Panel = styled(motion.div)`
  background: white;
  border-radius: 24px;
  width: 90%;
  max-width: 900px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  padding: 24px 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const CloseButton = styled.button`
  background: rgba(255, 255, 255, 0.2);
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.3);
    transform: scale(1.05);
  }
`;

const TabBar = styled.div`
  display: flex;
  border-bottom: 1px solid #e0e0e0;
  background: #f8f9fa;
`;

const Tab = styled.button`
  flex: 1;
  padding: 16px;
  border: none;
  background: ${props => props.active ? 'white' : 'transparent'};
  color: ${props => props.active ? '#667eea' : '#666'};
  font-weight: ${props => props.active ? '600' : '400'};
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 2px solid ${props => props.active ? '#667eea' : 'transparent'};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  
  &:hover {
    background: white;
  }
`;

const Content = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 32px;
`;

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const RoleGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
`;

const RoleCard = styled(motion.div)`
  padding: 20px;
  border-radius: 16px;
  border: 2px solid ${props => props.selected ? '#667eea' : '#e0e0e0'};
  background: ${props => props.selected ? 'rgba(102, 126, 234, 0.05)' : 'white'};
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  }
`;

const RoleIcon = styled.div`
  font-size: 2rem;
  margin-bottom: 8px;
`;

const RoleName = styled.div`
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
`;

const RoleDescription = styled.div`
  font-size: 0.85rem;
  color: #666;
  line-height: 1.4;
`;

const InputGroup = styled.div`
  margin-bottom: 24px;
`;

const Label = styled.label`
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  font-size: 0.95rem;
`;

const Input = styled.input`
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

// TextArea removed - not used

const SliderGroup = styled.div`
  margin-bottom: 24px;
`;

const SliderLabel = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
`;

const SliderValue = styled.span`
  color: #667eea;
  font-weight: 600;
`;

const Slider = styled.input`
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  outline: none;
  -webkit-appearance: none;
  
  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      transform: scale(1.2);
    }
  }
  
  &::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
    border: none;
  }
`;

const ToggleGroup = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 10px;
  margin-bottom: 16px;
`;

const ToggleLabel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const ToggleName = styled.div`
  font-weight: 500;
  color: #333;
`;

const ToggleDescription = styled.div`
  font-size: 0.85rem;
  color: #666;
`;

const Toggle = styled.button`
  width: 60px;
  height: 32px;
  border-radius: 16px;
  border: none;
  background: ${props => props.active ? '#667eea' : '#ddd'};
  cursor: pointer;
  position: relative;
  transition: all 0.3s;
  
  &::after {
    content: '';
    position: absolute;
    top: 4px;
    left: ${props => props.active ? '32px' : '4px'};
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: white;
    transition: all 0.3s;
  }
`;

const Footer = styled.div`
  padding: 20px 32px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const Button = styled(motion.button)`
  padding: 12px 24px;
  border-radius: 10px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
`;

const PrimaryButton = styled(Button)`
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const SecondaryButton = styled(Button)`
  background: #f0f0f0;
  color: #333;
  
  &:hover {
    background: #e0e0e0;
  }
`;

const PersonalizationPanel = ({ isOpen, onClose, userId }) => {
  const [activeTab, setActiveTab] = useState('role');
  const [loading, setLoading] = useState(false);
  const [roleTemplates, setRoleTemplates] = useState([]);
  const [config, setConfig] = useState({
    role: '温暖倾听者',
    role_name: '心语',
    personality: '温暖耐心',
    tone: '温和',
    style: '简洁',
    formality: 0.3,
    enthusiasm: 0.5,
    empathy_level: 0.8,
    humor_level: 0.3,
    response_length: 'medium',
    use_emoji: false,
    learning_mode: true,
    safety_level: 'standard'
  });

  useEffect(() => {
    if (isOpen && userId) {
      loadConfig();
      loadRoleTemplates();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, userId]);

  const loadRoleTemplates = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/personalization/templates`);
      setRoleTemplates(response.data);
    } catch (error) {
      console.error('加载角色模板失败:', error);
    }
  };

  const loadConfig = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE}/api/personalization/config/${userId}`);
      if (response.data.config) {
        setConfig(response.data.config);
      }
    } catch (error) {
      console.error('加载配置失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      await axios.post(`${API_BASE}/api/personalization/config/${userId}`, config);
      alert('配置保存成功！');
      onClose();
    } catch (error) {
      console.error('保存配置失败:', error);
      alert('保存失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const applyTemplate = async (templateId) => {
    try {
      setLoading(true);
      const response = await axios.post(
        `${API_BASE}/api/personalization/config/${userId}/apply-template?template_id=${templateId}`
      );
      if (response.data.config) {
        setConfig(response.data.config);
      }
      alert('模板应用成功！');
    } catch (error) {
      console.error('应用模板失败:', error);
      alert('应用模板失败，请稍后重试');
    } finally {
      setLoading(false);
    }
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
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          onClick={(e) => e.stopPropagation()}
        >
          <Header>
            <Title>
              <Sparkles size={24} />
              AI形象定制中心
            </Title>
            <CloseButton onClick={onClose}>
              <X size={20} />
            </CloseButton>
          </Header>

          <TabBar>
            <Tab active={activeTab === 'role'} onClick={() => setActiveTab('role')}>
              <User size={18} />
              角色选择
            </Tab>
            <Tab active={activeTab === 'style'} onClick={() => setActiveTab('style')}>
              <MessageCircle size={18} />
              风格调节
            </Tab>
            <Tab active={activeTab === 'advanced'} onClick={() => setActiveTab('advanced')}>
              <Settings size={18} />
              高级设置
            </Tab>
          </TabBar>

          <Content>
            {activeTab === 'role' && (
              <Section>
                <SectionTitle>
                  <Bot size={20} />
                  选择AI角色
                </SectionTitle>
                <RoleGrid>
                  {roleTemplates.map((template) => (
                    <RoleCard
                      key={template.id}
                      selected={config.role === template.role}
                      onClick={() => applyTemplate(template.id)}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <RoleIcon>{template.icon}</RoleIcon>
                      <RoleName>{template.name}</RoleName>
                      <RoleDescription>{template.description}</RoleDescription>
                    </RoleCard>
                  ))}
                </RoleGrid>

                <Section style={{ marginTop: '32px' }}>
                  <SectionTitle>自定义设置</SectionTitle>
                  <InputGroup>
                    <Label>AI名称</Label>
                    <Input
                      value={config.role_name}
                      onChange={(e) => setConfig({ ...config, role_name: e.target.value })}
                      placeholder="给AI起个名字..."
                    />
                  </InputGroup>
                </Section>
              </Section>
            )}

            {activeTab === 'style' && (
              <Section>
                <SectionTitle>
                  <Zap size={20} />
                  表达风格
                </SectionTitle>

                <SliderGroup>
                  <SliderLabel>
                    <Label>正式程度</Label>
                    <SliderValue>{(config.formality * 100).toFixed(0)}%</SliderValue>
                  </SliderLabel>
                  <Slider
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.formality}
                    onChange={(e) => setConfig({ ...config, formality: parseFloat(e.target.value) })}
                  />
                </SliderGroup>

                <SliderGroup>
                  <SliderLabel>
                    <Label>活泼度</Label>
                    <SliderValue>{(config.enthusiasm * 100).toFixed(0)}%</SliderValue>
                  </SliderLabel>
                  <Slider
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.enthusiasm}
                    onChange={(e) => setConfig({ ...config, enthusiasm: parseFloat(e.target.value) })}
                  />
                </SliderGroup>

                <SliderGroup>
                  <SliderLabel>
                    <Label>共情程度</Label>
                    <SliderValue>{(config.empathy_level * 100).toFixed(0)}%</SliderValue>
                  </SliderLabel>
                  <Slider
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.empathy_level}
                    onChange={(e) => setConfig({ ...config, empathy_level: parseFloat(e.target.value) })}
                  />
                </SliderGroup>

                <SliderGroup>
                  <SliderLabel>
                    <Label>幽默程度</Label>
                    <SliderValue>{(config.humor_level * 100).toFixed(0)}%</SliderValue>
                  </SliderLabel>
                  <Slider
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={config.humor_level}
                    onChange={(e) => setConfig({ ...config, humor_level: parseFloat(e.target.value) })}
                  />
                </SliderGroup>

                <ToggleGroup>
                  <ToggleLabel>
                    <ToggleName>使用Emoji表情</ToggleName>
                    <ToggleDescription>让回复更加生动活泼</ToggleDescription>
                  </ToggleLabel>
                  <Toggle
                    active={config.use_emoji}
                    onClick={() => setConfig({ ...config, use_emoji: !config.use_emoji })}
                  />
                </ToggleGroup>
              </Section>
            )}

            {activeTab === 'advanced' && (
              <Section>
                <SectionTitle>
                  <Settings size={20} />
                  高级设置
                </SectionTitle>

                <ToggleGroup>
                  <ToggleLabel>
                    <ToggleName>学习模式</ToggleName>
                    <ToggleDescription>AI会根据你的反馈自动优化</ToggleDescription>
                  </ToggleLabel>
                  <Toggle
                    active={config.learning_mode}
                    onClick={() => setConfig({ ...config, learning_mode: !config.learning_mode })}
                  />
                </ToggleGroup>

                <InputGroup>
                  <Label>安全级别</Label>
                  <div style={{ display: 'flex', gap: '12px' }}>
                    {['strict', 'standard', 'relaxed'].map((level) => (
                      <Button
                        key={level}
                        onClick={() => setConfig({ ...config, safety_level: level })}
                        style={{
                          flex: 1,
                          background: config.safety_level === level ? '#667eea' : '#f0f0f0',
                          color: config.safety_level === level ? 'white' : '#333'
                        }}
                      >
                        {level === 'strict' ? '严格' : level === 'standard' ? '标准' : '宽松'}
                      </Button>
                    ))}
                  </div>
                </InputGroup>
              </Section>
            )}
          </Content>

          <Footer>
            <SecondaryButton onClick={onClose}>
              取消
            </SecondaryButton>
            <PrimaryButton onClick={handleSave} disabled={loading}>
              <Check size={18} />
              {loading ? '保存中...' : '保存配置'}
            </PrimaryButton>
          </Footer>
        </Panel>
      </Overlay>
    </AnimatePresence>
  );
};

export default PersonalizationPanel;












