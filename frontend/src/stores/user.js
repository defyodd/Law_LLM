import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserInfoStore = defineStore('userInfo', () => {
  const userInfo = ref({
    userId: '',
    userName: '',
    avatar: ''
  })

  const setUserInfo = (newUserInfo) => {
    userInfo.value = { ...userInfo.value, ...newUserInfo }
  }

  const removeUserInfo = () => {
    userInfo.value = {
      userId: '',
      userName: '',
      avatar: ''
    }
  }

  return {
    userInfo,
    setUserInfo,
    removeUserInfo
  }
}, {
  persist: true
})

export default useUserInfoStore
