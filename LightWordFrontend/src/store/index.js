import Vue from 'vue'
import vuex from 'vuex'
Vue.use(vuex);


import auth from './auth'
import theme from './theme'

export default new vuex.Store({
    modules:{
        auth,
        theme
    },

})