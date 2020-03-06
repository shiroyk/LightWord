import axios from 'axios'
import router from '@/router'
import store from '@/store'

if (process.env.NODE_ENV == 'development') {    
  axios.defaults.baseURL = 'http://127.0.0.1';
} else if (process.env.NODE_ENV == 'production') {    
  axios.defaults.baseURL = 'http://api.shiroyk.moe';
}

axios.defaults.timeout = 5000
axios.defaults.retry = 2
axios.defaults.retryDelay = 100
// axios.defaults.headers.common['Content-Type'] = 'application/json;charset=UTF-8'

axios.interceptors.request.use(
  config => {
      const token = store.state.auth.token;

      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config;
  },
  err => {
      return Promise.reject(err);
  }
);

axios.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if(error.response) {
      switch  (error.response.status) {
        case 401:
          if (router.currentRoute.path != '/') {
            store.commit("removeToken")
            router.replace({ path: '/' })
          }
          break

        case 403:
          router.back()
          break
  
        case 404:
          router.back()
          break
        
        case 500:
          router.back()
          break
          }    
    } else {
    console.log(error.message)
  }
  return Promise.reject(error)
})

export default axios