import dialog from './dialog.vue'

function initDialog(Vue, options = {}) {
  const vuetify = options.vuetify
  const router = options.router

  const Dialogs = Vue.extend(Object.assign({ vuetify, router }, dialog))
  function createDialogCmp(options) {
    const app = document.createElement('div')
    let vm = new Dialogs({ el: document.createElement('div') });
    options.messageDialog = true
    Object.assign(vm, options);
    return new Promise(resolve => {
      vm.$on('dialog', (status) => {
        if (!status) {
          vm.$nextTick(() => {
            vm.$destroy()
            app.removeChild(vm.$el)
          })
        }
        resolve(app.appendChild(vm.$mount().$el))
        if (options.push) {
          router.push(options.push)
        }
      })
    })
  }

  function show(title, options = {}) {
    options.title = title
    return createDialogCmp(options)
  }

  Vue.prototype.$dialog = show
  Vue.prototype.$dialog.options = options || {}
}


export default initDialog