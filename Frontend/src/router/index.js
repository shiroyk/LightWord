import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'
import Index from '@/components/index'
import Home from '@/components/home'
import Help from '@/components/help'
import Setting from '@/components/settings/setting'
import Practice from '@/components/resource/practice'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'index',
      component: Index,
      meta: {
        title: 'LightWord',
        color: '#844357',
      }
    },
    {
      path: '/home',
      name: 'home',
      component: Home,
      meta: {
        title: 'Home',
        requireAuth: true,
        color: '#1565C0'
      }
    },
    {
      path: '/help',
      name: 'help',
      component: Help,
      meta: {
        title: 'Help',
        requireAuth: true,
        color: '#1565C0'
      }
    },
    {
      path: '/practice',
      name: 'practice',
      component: Practice,
      meta: {
        title: 'Practice',
        requireAuth: true,
        color: '#1565C0'
      }
    },
    {
      path: '/setting',
      name: 'setting',
      component: Setting,
      meta: {
        title: 'Setting',
        requireAuth: true,
        color: '#1565C0'
      }
    },
    {
      path: '*',
      redirect: '/'
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  if (to.meta.color) {
    document.querySelector("meta[name=theme-color]").setAttribute("content", to.meta.color)
  }
  if (to.meta.requireAuth) {
    const token = store.state.auth.token
    if (token) {
      store.dispatch("inspectToken", token)
        .then(() => next())
        .catch(() => (
          Vue.prototype.$dialog("登录信息已失效...", {
            color: "error",
            showClose: false,
            progress: "linear",
            push: "/"
          })))
    } else {
      console.log('未检测到token')
      router.replace({ path: '/' })
    }
  } else {
    next()
  }

})


export default router
