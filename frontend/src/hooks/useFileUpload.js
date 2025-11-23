import { useState, useRef } from 'react';
import { validateFile, getFileIcon } from '../utils/fileUtils';
import { formatFileSize } from '../utils/formatters';

export const useFileUpload = () => {
  const [attachments, setAttachments] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const validFiles = [];
    
    for (const file of files) {
      const validation = validateFile(file);
      if (!validation.valid) {
        validation.errors.forEach(error => alert(error));
        continue;
      }

      // 添加到有效文件列表
      validFiles.push({
        id: Date.now() + Math.random(),
        file,
        name: file.name,
        size: file.size,
        type: file.type
      });
    }

    if (validFiles.length > 0) {
      setAttachments(prev => [...prev, ...validFiles]);
    }

    // 清空input，允许重复上传同一文件
    event.target.value = '';
  };

  const removeAttachment = (attachmentId) => {
    setAttachments(prev => prev.filter(att => att.id !== attachmentId));
  };

  return {
    attachments,
    setAttachments,
    fileInputRef,
    handleFileUpload,
    removeAttachment,
    getFileIcon,
    formatFileSize
  };
};

