
const themeStore = {
  state: {
    theme: sessionStorage.getItem('theme'),
  },
  getters: {},
  mutations: {
    setTheme(state, name) {
      sessionStorage.setItem('theme', name);
      state.theme = name;
    }
  },
}

export default themeStore
