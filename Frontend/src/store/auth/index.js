import axios from 'axios'
import cookies from 'vue-cookies'
import jwt_decode from 'jwt-decode'

const authStore = {
  state: {
    token: cookies.get('QWQT'),
    login: {
      messages: [],
    },
    register: {
      messages: [],
    },
    resetpass:{
      messages: [],
    }
  },
  getters: {},
  mutations: {
    updateToken(state, newToken) {
      cookies.set('QWQT', newToken);
      state.token = newToken;
    },
    removeToken(state) {
      cookies.remove('QWQT');
      state.token = null;
    },
    loginMessage(state, messages) {
      state.login.messages = messages
    }
  },
  actions: {
    login({commit}, user) {
      return new Promise((resolve, reject) => { 
        axios.post('/token', {},{
            auth: user
          }).then(response => {
            if (response.status == 200) {
              commit('updateToken', response.data.token);
            }
            resolve(response)
          })
          .catch(error => {
            if (error.response.status == 401) {
              commit('loginMessage', 'Invalid username or password.')
              commit('removeToken')
            }
            reject(error)
          })
        })
    },
    logout({commit}) {
      return new Promise(() => {
        commit('removeToken')
      })
    },
    refreshToken({commit}) {
      return new Promise((resolve, reject) => { 
        axios.get('token/refresh', this.state.token)
          .then((response) => {
            if (response.status == 200) {
              commit('updateToken', response.data.token)
            }
            resolve(response)
          })
          .catch(() => {reject()})
        })
    },
    inspectToken({commit}, token){
      if (token) {
        const decoded = jwt_decode(token);
        const exp = decoded.exp
        const iat = decoded.iat
        const datenow = Date.now()
        
        if(exp - (datenow/1000) < 3600 && (datenow/1000) - iat < 82800){
          //在1小时内过期且不超过使用寿命，则刷新
          this.dispatch('refreshToken')
          console.log('刷新token')
        } else if ((datenow/1000) > exp) {
          console.log('过期token')
          commit('removeToken')
        }
      }
    }
  },
}

export default authStore
