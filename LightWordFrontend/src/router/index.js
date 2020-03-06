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
        title: 'LightWord'
      }
    },
    {
      path: '/home',
      name: 'home',
      component: Home,
      meta: {
        title: 'Home',
        requireAuth: true
      }
    },
    {
      path: '/help',
      name: 'help',
      component: Help,
      meta: {
        title: 'Help',
        requireAuth: true
      }
    },
    {
      path: '/practice',
      name: 'practice',
      component: Practice,
      meta: {
        title: 'Practice',
        requireAuth: true
      }
    },
    {
      path: '/setting',
      name: 'setting',
      component: Setting,
      meta: {
        title: 'Setting',
        requireAuth: true
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  if (to.meta.requireAuth) {
    const token = store.state.auth.token
    if (token) {
      store.dispatch("inspectToken", token)
      .then(() => next())
      .catch(() => router.replace({ path: '/' }))
      console.log('检查token')
    } else {
      console.log('未检测到token')
      router.replace({ path: '/' })
    }
  } else {
    next()
  }

})


export default router
