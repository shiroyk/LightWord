import dialog from './dialog.vue'

function initDialog(Vue, options = {}) {
  const vuetify = options.vuetify
  const router = options.router

  const Dialogs = Vue.extend(Object.assign({ vuetify, router }, dialog))
  function createDialogCmp(options) {
    const container = document.createElement('div')
    let vm = new Dialogs();
    options.messageDialog = true
    Object.assign(vm, options);
    container.appendChild(vm.$mount().$el)
    
    return vm
  }

  function show(title, options = {}) {
    options.title = title
    const vm = createDialogCmp(options)
    vm.$on('dialog', (status) => {
      if (!status) {
        vm.$nextTick(() => {
          vm.$destroy()
        })
      }
      if (options.push) {
        router.push(options.push)
      }
    })
  }

  Vue.prototype.$dialog = Object.assign(show, { options })

}

export default initDialog