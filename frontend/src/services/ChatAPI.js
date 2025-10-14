import axios from 'axios';

// Use external server IP for external access
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://8.130.162.82:8000';

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
      const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}/history`, {
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
      const response = await axios.get(`${API_BASE_URL}/sessions/${sessionId}/summary`);
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
      const response = await axios.get(`${API_BASE_URL}/users/${userId}/sessions`, {
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
      const response = await axios.delete(`${API_BASE_URL}/sessions/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('删除会话失败:', error);
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
}

export default ChatAPI;
