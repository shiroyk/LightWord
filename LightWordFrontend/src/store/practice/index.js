const practiceStore = {
    state: {
      volume: sessionStorage.getItem('volume'),
      target: sessionStorage.getItem('target'),
    },
    getters: {},
    mutations: {
      setVolume(state, status) {
        sessionStorage.setItem('volume', status);
        state.volume = status;
      },
      setTarget(state, num) {
        sessionStorage.setItem('target', num);
        state.target = num
      }
    },
  }
  
  export default practiceStore  