// 格式化时间戳（用于消息）
export const formatTimestamp = (date) => {
  if (!date) return '';
  const now = new Date();
  const messageDate = new Date(date);
  const diffMs = now - messageDate;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}小时前`;
  
  return messageDate.toLocaleString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 格式化相对时间（用于会话列表）
export const formatRelativeTime = (date) => {
  if (!date) return '';
  const now = new Date();
  const targetDate = new Date(date);
  const diffMs = now - targetDate;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);
  
  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays === 1) return '昨天';
  if (diffDays < 7) return `${diffDays}天前`;
  if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return `${weeks}周前`;
  }
  if (diffDays < 365) {
    const months = Math.floor(diffDays / 30);
    return `${months}个月前`;
  }
  
  // 超过一年，显示具体日期
  return targetDate.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

// 格式化文件大小
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// URL检测函数
export const detectURLs = (text) => {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  return text.match(urlRegex) || [];
};

