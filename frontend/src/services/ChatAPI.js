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

  /**
   * 流式发送消息（SSE），支持附件。
   * @param {FormData} formData 包含 message, user_id, session_id, files 等
   * @param {function} onToken  每收到一个 token 时回调 (tokenString)
   * @param {function} onDone   完成时回调 ({session_id, emotion, suggestions})
   * @param {function} onError  出错时回调 (errorString)
   * @returns {function} abort  调用可取消请求
   */
  static sendMessageStreaming(formData, { onToken, onDone, onError }) {
    const controller = new AbortController();

    (async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/stream`, {
          method: 'POST',
          body: formData,
          signal: controller.signal,
        });

        if (!response.ok) {
          const errText = await response.text();
          onError && onError(`服务器错误 (${response.status}): ${errText}`);
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop(); // keep incomplete line

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') continue;
            try {
              const data = JSON.parse(payload);
              if (data.type === 'token' && data.content) {
                onToken && onToken(data.content);
              } else if (data.type === 'done') {
                onDone && onDone(data);
              } else if (data.type === 'error') {
                onError && onError(data.content || '未知错误');
              }
            } catch {
              // ignore parse errors for partial data
            }
          }
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          onError && onError(err.message || '网络错误');
        }
      }
    })();

    return () => controller.abort();
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
      const response = await axios.post(`${API_BASE_URL}/chat/parse-url`, data, {
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

  static async getUserMemories(userId, limit = 3) {
    const response = await axios.get(`${API_BASE_URL}/memory/users/${userId}/memories`, {
      params: { limit }
    });
    return response.data;
  }

  static async searchUserMemories(userId, query, limit = 5) {
    const response = await axios.get(`${API_BASE_URL}/memory/users/${userId}/memories/search`, {
      params: { query, n_results: limit, days_limit: 3650 }
    });
    return response.data;
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

  // Skills/Tools
  static async getAvailableSkills() {
    try {
      const response = await axios.get(`${API_BASE_URL}/agent/tools`);
      const payload = response.data;
      return {
        tools: payload?.data?.tools || payload?.tools || []
      };
    } catch (error) {
      console.error('获取技能列表失败:', error);
      // Return default skills if API is unavailable
      return {
        tools: [
          { name: 'search_memory', category: 'memory', description: '搜索历史记忆和对话' },
          { name: 'get_emotion_log', category: 'emotion', description: '查看情绪变化趋势' },
          { name: 'recommend_meditation', category: 'resource', description: '推荐冥想和放松资源' },
          { name: 'psychological_assessment', category: 'assessment', description: '心理状态快速评估' },
          { name: 'set_reminder', category: 'scheduler', description: '设置提醒和日程' },
          { name: 'get_user_mood_trend', category: 'emotion', description: '分析近期情绪模式' },
        ]
      };
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
