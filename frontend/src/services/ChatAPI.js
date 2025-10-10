import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8008';

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
