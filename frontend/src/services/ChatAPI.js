import axios from 'axios';

// Use local server for development, external server for production
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ChatAPI {
  static async sendMessage(data) {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('发送消息失败:', error);
      throw error;
    }
  }

  static async sendMessageWithAttachments(formData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat/with-attachments`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('发送带附件的消息失败:', error);
      throw error;
    }
  }

  static async submitFeedback(feedbackData) {
    try {
      const response = await axios.post(`${API_BASE_URL}/feedback`, feedbackData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('提交反馈失败:', error);
      throw error;
    }
  }

  static async getFeedbackStatistics() {
    try {
      const response = await axios.get(`${API_BASE_URL}/feedback/statistics`);
      return response.data;
    } catch (error) {
      console.error('获取反馈统计失败:', error);
      throw error;
    }
  }

  static async parseURL(data) {
    try {
      const response = await axios.post(`${API_BASE_URL}/parse-url`, data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('URL解析失败:', error);
      throw error;
    }
  }

  static async getSessionHistory(sessionId, limit = 20) {
    try {
      const response = await axios.get(`${API_BASE_URL}/chat/sessions/${sessionId}/history`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('获取会话历史失败:', error);
      throw error;
    }
  }

  static async getSessionSummary(sessionId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/chat/sessions/${sessionId}/summary`);
      return response.data;
    } catch (error) {
      console.error('获取会话摘要失败:', error);
      throw error;
    }
  }

  static async addKnowledge(text, category = 'general') {
    try {
      const response = await axios.post(`${API_BASE_URL}/knowledge`, {
        text,
        category
      });
      return response.data;
    } catch (error) {
      console.error('添加知识失败:', error);
      throw error;
    }
  }

  static async addEmotionExample(text, emotion, intensity) {
    try {
      const response = await axios.post(`${API_BASE_URL}/emotion-examples`, {
        text,
        emotion,
        intensity
      });
      return response.data;
    } catch (error) {
      console.error('添加情感示例失败:', error);
      throw error;
    }
  }

  static async getUserSessions(userId, limit = 50) {
    try {
      const response = await axios.get(`${API_BASE_URL}/chat/users/${userId}/sessions`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('获取用户会话列表失败:', error);
      throw error;
    }
  }

  static async deleteSession(sessionId) {
    try {
      const response = await axios.delete(`${API_BASE_URL}/chat/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('删除会话失败:', error);
      throw error;
    }
  }

  static async searchUserSessions(userId, keyword = '', limit = 50) {
    try {
      const response = await axios.get(`${API_BASE_URL}/chat/users/${userId}/sessions/search`, {
        params: { keyword, limit }
      });
      return response.data;
    } catch (error) {
      console.error('搜索用户会话失败:', error);
      throw error;
    }
  }

  static async deleteSessionsBatch(sessionIds) {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat/sessions/batch-delete`, sessionIds, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('批量删除会话失败:', error);
      throw error;
    }
  }

  static async healthCheck() {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('健康检查失败:', error);
      throw error;
    }
  }

  // 多模态功能
  static async sendMultimodalMessage(data) {
    try {
      const response = await axios.post(`${API_BASE_URL}/multimodal/chat`, data, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.data;
    } catch (error) {
      console.error('发送多模态消息失败:', error);
      throw error;
    }
  }

  static async transcribeAudio(audioBlob) {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'audio.wav');

      const response = await axios.post(`${API_BASE_URL}/multimodal/audio/transcribe`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('语音识别失败:', error);
      throw error;
    }
  }

  static async analyzeImage(imageBlob) {
    try {
      const formData = new FormData();
      formData.append('image_file', imageBlob, 'image.jpg');

      const response = await axios.post(`${API_BASE_URL}/multimodal/image/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('图像分析失败:', error);
      throw error;
    }
  }
}

export default ChatAPI;
