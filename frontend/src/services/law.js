// 导入request.js请求工具
import request from '@/utils/request.js'

// 提供调用添加法律法规接口的函数
export const addLaw = (lawData) => {
    // 借助UrlSearchParams完成传递
    const params = new URLSearchParams()
    for (let key in lawData) {
        params.append(key, lawData[key]);
    }
    return request.post('/law/add', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
}

// 提供调用上传法律法规JSON文件接口的函数
export const uploadLawJson = (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return request.post('/law/upload', formData);
}

// 提供调用获取法律法规详情接口的函数
export const getLawInfo = (lawId) => {
    return request.get('/law/getLawInfo?lawId=' + lawId);
}

// 提供调用获取所有法律法规列表接口的函数
export const getAllLaws = () => {
    return request.get('/law/getAllLaws');
}

// 提供调用搜索法律法规接口的函数
export const searchLaws = (keyword) => {
    return request.get('/law/search?keyword=' + encodeURIComponent(keyword));
}