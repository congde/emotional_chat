import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { Mic, Image as ImageIcon, Send, Loader2, Volume2 } from 'lucide-react';

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
`;

const InputRow = styled.div`
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

const TextArea = styled.textarea`
  flex: 1;
  padding: 12px 16px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  outline: none;
  transition: all 0.2s ease;
  min-height: 50px;
  max-height: 200px;

  &:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }

  &::placeholder {
    color: #999;
  }
`;

const Button = styled.button`
  padding: 12px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: ${props => props.primary ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'rgba(102, 126, 234, 0.1)'};
  color: ${props => props.primary ? 'white' : '#667eea'};
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.recording {
    background: #ef4444;
    color: white;
    animation: pulse 1.5s ease-in-out infinite;
  }
`;

const PulsingCircle = styled.div`
  width: 12px;
  height: 12px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse 1.5s ease-in-out infinite;
`;

const FileInput = styled.input`
  display: none;
`;

const MediaPreview = styled.div`
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
`;

const ImagePreview = styled.div`
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  width: 80px;
  height: 80px;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  button {
    position: absolute;
    top: 4px;
    right: 4px;
    background: rgba(0, 0, 0, 0.6);
    color: white;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;

    &:hover {
      background: rgba(0, 0, 0, 0.8);
    }
  }
`;

const AudioPreview = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  color: #667eea;
  font-size: 14px;
`;

const InfoText = styled.div`
  padding: 8px 12px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 8px;
  color: #667eea;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MultimodalInput = ({ onSend, disabled }) => {
  const [text, setText] = useState('');
  const [images, setImages] = useState([]);
  const [audioBlob, setAudioBlob] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioDuration, setAudioDuration] = useState(0);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  // 开始录音
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        
        // 停止所有音频轨道
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);

      // 计时器
      let seconds = 0;
      timerRef.current = setInterval(() => {
        seconds++;
        setAudioDuration(seconds);
      }, 1000);

    } catch (error) {
      console.error('录音失败:', error);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  // 停止录音
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }
  };

  // 取消录音
  const cancelRecording = () => {
    stopRecording();
    setAudioBlob(null);
    setAudioUrl(null);
    setAudioDuration(0);
  };

  // 选择图片
  const handleImageSelect = (event) => {
    const files = Array.from(event.target.files);
    const imageFiles = files.filter(file => file.type.startsWith('image/'));
    
    imageFiles.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImages(prev => [...prev, { file, url: reader.result }]);
      };
      reader.readAsDataURL(file);
    });
    
    event.target.value = ''; // 重置input
  };

  // 删除图片
  const removeImage = (index) => {
    setImages(prev => prev.filter((_, i) => i !== index));
  };

  // 播放音频预览
  const playAudio = () => {
    if (audioUrl) {
      const audio = new Audio(audioUrl);
      audio.play();
    }
  };

  // 格式化时长
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // 发送消息
  const handleSend = async () => {
    if ((!text && !images.length && !audioBlob) || disabled) {
      return;
    }

    try {
      onSend({
        text: text || undefined,
        images: images.map(img => img.file),
        audioBlob: audioBlob
      });

      // 清空输入
      setText('');
      setImages([]);
      setAudioBlob(null);
      setAudioUrl(null);
      setAudioDuration(0);
    } catch (error) {
      console.error('发送失败:', error);
    }
  };

  // 处理键盘事件
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // 清理
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [audioUrl]);

  return (
    <InputContainer>
      <InputRow>
        <TextArea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入消息或点击麦克风开始录音..."
          rows={1}
        />
        
        <Button
          onClick={() => isRecording ? stopRecording() : startRecording()}
          disabled={disabled && !isRecording}
          className={isRecording ? 'recording' : ''}
          title={isRecording ? '点击停止录音' : '点击开始录音'}
        >
          {isRecording ? (
            <PulsingCircle />
          ) : (
            <Mic size={20} />
          )}
        </Button>

        <Button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          title="上传图片"
        >
          <ImageIcon size={20} />
        </Button>

        <Button
          onClick={handleSend}
          disabled={disabled || (!text && !images.length && !audioBlob)}
          primary
          title="发送"
        >
          <Send size={20} />
        </Button>
      </InputRow>

      {/* 图片预览 */}
      {images.length > 0 && (
        <MediaPreview>
          {images.map((img, index) => (
            <ImagePreview key={index}>
              <img src={img.url} alt={`Preview ${index}`} />
              <button onClick={() => removeImage(index)}>×</button>
            </ImagePreview>
          ))}
        </MediaPreview>
      )}

      {/* 音频预览 */}
      {audioBlob && (
        <AudioPreview>
          <Volume2 size={16} />
          <span>{formatDuration(audioDuration)}</span>
          <Button
            onClick={playAudio}
            style={{ padding: '4px 8px', fontSize: '12px' }}
          >
            播放
          </Button>
          <Button
            onClick={cancelRecording}
            style={{ padding: '4px 8px', fontSize: '12px', background: '#ef4444', color: 'white' }}
          >
            删除
          </Button>
        </AudioPreview>
      )}

      {isRecording && (
        <InfoText>
          <PulsingCircle style={{ width: '8px', height: '8px' }} />
          正在录音... {formatDuration(audioDuration)}
        </InfoText>
      )}

      <FileInput
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleImageSelect}
      />
    </InputContainer>
  );
};

export default MultimodalInput;
