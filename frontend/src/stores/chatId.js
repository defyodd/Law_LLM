import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatIdStore = defineStore('chatId', () => {
  const chatId = ref('')

  const setChatId = (newChatId) => {
    chatId.value = newChatId
  }

  const removeChatId = () => {
    chatId.value = ''
  }

  return {
    chatId,
    setChatId,
    removeChatId
  }
}, {
  persist: true
})

export default useChatIdStore
