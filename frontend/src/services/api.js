import request from '@/utils/request.js'
import { useTokenStore } from '@/stores/token.js'

export const chatAPI = {
  // 新建对话 - 使用 x-www-form-urlencoded
  async createNewChat(userId, title, type) {
    try {
      if (!userId) {
        throw new Error('userId is required');
      }

      // 使用 URLSearchParams 构造 x-www-form-urlencoded 数据
      const params = new URLSearchParams();
      params.append('userId', userId);
      params.append('title', title);
      params.append('type', type);

      // 发起 POST 请求
      const response = await request.post('ai/create', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      if (response.code !== 0) {
        throw new Error(`API Error: ${response.message}`);
      }

      // 返回 historyId 字段
      return response.data.historyId;
    } catch (error) {
      console.error('Create chat error:', error);
      throw error;
    }
  },

  // 重命名对话 - 使用 x-www-form-urlencoded
  async renameChat(historyId, newTitle) {
    try {
      if (!historyId) {
        throw new Error('historyId is required');
      }
      if (!newTitle) {
        throw new Error('newTitle is required');
      }

      const params = new URLSearchParams();
      params.append('historyId', historyId);
      params.append('newTitle', newTitle);

      // 发起 PATCH 请求
      const response = await request.patch('/ai/rename', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      if (response.code !== 0) {
        throw new Error(`API Error: ${response.message}`);
      }

      return response.data;
    } catch (error) {
      console.error('Rename chat error:', error);
      throw error;
    }
  },

  // 删除对话 - 使用 x-www-form-urlencoded
  async deleteChat(historyId) {
    try {
      if (!historyId) {
        throw new Error('historyId is required');
      }

      const params = new URLSearchParams();
      params.append('historyId', historyId);

      // 发起 DELETE 请求
      const response = await request.delete('/ai/delete', {
        data: params,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });

      if (response.code !== 0) {
        throw new Error(`API Error: ${response.message}`);
      }

      return response.data;
    } catch (error) {
      console.error('Delete chat error:', error);
      throw error;
    }
  },

  // 发送聊天消息
  async sendMessage(data, historyId, model) {
    try {
      let url = '/ai/chat';
      
      // 准备请求数据
      let requestData;
      if (data instanceof FormData) {
        requestData = data;
        // 为 FormData 添加 historyId 和 model
        if (historyId) {
          requestData.append('historyId', historyId);
        }
        if (model) {
          requestData.append('model', model);
        }
      } else {
        requestData = new URLSearchParams();
        requestData.append('prompt', data);
        if (historyId) {
          requestData.append('historyId', historyId);
        }
        if (model) {
          requestData.append('model', model);
        }
      }
      
      const tokenStore = useTokenStore();
      const headers = {};
      
      if (tokenStore.token) {
        headers.Authorization = tokenStore.token;
      }
      
      // 设置请求头
      if (data instanceof FormData) {
      } else {
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
      }
      
      // 发送请求
      const response = await fetch(`${request.defaults.baseURL}${url}`, {
        method: 'POST',
        headers,
        body: requestData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      // 创建一个用于处理流数据的方法，可以检测reference信息
      return {
        reader,
        referenceInfo: { value: null }, // 引用对象，用于存储reference值
        async read(callback) {
          let buffer = '';
          let referenceFound = false;
          let accumulatedContent = ''; // 添加累积内容变量
          
          try {
            while (true) {
              const { done, value } = await reader.read();
              
              if (done) break;
              
              // 解码接收到的数据
              const chunk = new TextDecoder().decode(value);
              buffer += chunk;
              accumulatedContent += chunk; // 累积所有内容
              
              // 检查是否包含reference信息
              const referenceMatch = buffer.match(/<!-- REFERENCE_DATA:([\s\S]*?) -->/);
              if (referenceMatch) {
                // 提取reference信息
                this.referenceInfo.value = referenceMatch[1].trim();
                // 从累积内容和当前缓冲区中移除reference标记
                accumulatedContent = accumulatedContent.replace(/<!-- REFERENCE_DATA:([\s\S]*?) -->/, '');
                // 移除reference标记
                buffer = buffer.replace(/<!-- REFERENCE_DATA:([\s\S]*?) -->/, '');
                referenceFound = true;
              }
              
              // 回调提供处理后的内容
              callback({
                content: accumulatedContent,
                done: false,
                referenceFound,
                reference: this.referenceInfo.value
              });
              
              // 清空已处理的缓冲区
              buffer = '';
            }
            
            // 流结束
            callback({
              content: accumulatedContent,
              done: true,
              referenceFound,
              reference: this.referenceInfo.value
            });
          } catch (error) {
            console.error('Error reading stream:', error);
            throw error;
          }
        }
      };
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // 获取聊天记录列表 - 使用 URLSearchParams 查询参数
  async getChatHistory(userId, type) {
    try {
      // 构造URL参数
      const params = new URLSearchParams();
      
      // 添加userId参数（如果提供）
      if (userId) {
        params.append('userId', userId);
      }
      
      // 添加type参数（如果提供）
      if (type) {
        params.append('type', type);
      }
      
      // 构建完整URL
      let url = '/ai/getHistory';
      const queryString = params.toString();
      if (queryString) {
        url = `${url}?${queryString}`;
      }
      
      const response = await request.get(url);
      const result = response; // request.js 已经处理了 .data 部分
      
      if (result.code !== 0) {
        throw new Error(`API Error: ${result.message}`);
      }

      // 转换为前端需要的格式
      return result.data.map(item => ({
        id: item.historyId,
        title: item.title
      }));
    } catch (error) {
      console.error('API Error:', error);
      return [];
    }
  },

  // 获取特定对话的消息历史 - 使用 URLSearchParams 查询参数
  async getChatMessages(chatId) {
    try {
      // 构造请求URL，使用新的getChatInfo接口
      const response = await request.get(`/ai/getChatInfo?historyId=${chatId}`);

      // 检查响应状态
      if (response.code !== 0) {
        throw new Error(`API Error: ${response.message}`);
      }
      
      // 转换数据格式为ChatMessage组件期望的格式
      const messages = [];
      response.data.forEach(item => {
        // 添加用户消息
        messages.push({
          role: 'user',
          content: item.prompt,
          timestamp: new Date() // 使用当前时间作为临时时间戳
        });
        
        // 添加助手消息
        messages.push({
          role: 'assistant',
          content: item.answer,
          reference: item.reference, // 添加reference字段
          timestamp: new Date(new Date().getTime() + 1000) // 比用户消息晚1秒
        });
      });
      
      return messages;
    } catch (error) {
      console.error('获取聊天消息失败:', error);
      return [];
    }
  }
}

