import { Image, FileText } from 'lucide-react';

// 文件上传配置
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const allowedTypes = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'application/pdf',
  'text/plain',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
];

export const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf', '.txt', '.doc', '.docx'];

// 验证文件
export const validateFile = (file) => {
  const errors = [];
  
  // 验证文件大小
  if (file.size > MAX_FILE_SIZE) {
    errors.push(`文件 ${file.name} 太大，最大支持10MB`);
    return { valid: false, errors };
  }

  // 验证文件类型
  if (!allowedTypes.includes(file.type)) {
    // 也检查文件扩展名作为备用
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
      errors.push(`文件 ${file.name} 类型不支持。支持的类型：图片（JPG/PNG/GIF）、PDF、TXT、Word文档`);
      return { valid: false, errors };
    }
  }

  return { valid: true, errors: [] };
};

// 获取文件图标
export const getFileIcon = (fileType) => {
  if (fileType.startsWith('image/')) return <Image size={16} />;
  if (fileType === 'application/pdf') return <FileText size={16} />;
  return <FileText size={16} />;
};

