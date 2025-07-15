// 导入request.js请求工具
import request from '@/utils/request.js'

// 提供调用注册接口的函数 
export const userRegisterService = (registerData) => {
    // 借助UrlSerchParams完成传递
    const params = new URLSearchParams()
    for (let key in registerData) {
        params.append(key, registerData[key]);
    }
    return request.post('/auth/register', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
}

// 提供调用登录接口的函数
export const userLoginService = (loginData) => {
    // 借助UrlSerchParams完成传递
    const params = new URLSearchParams()
    for (let key in loginData) {
        params.append(key, loginData[key]);
    }
    return request.post('/auth/login', params, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });
}

// 提供调用获取用户信息接口的函数
export const userInfoService = () => {
    return request.get('/auth/getUserInfo');
}
