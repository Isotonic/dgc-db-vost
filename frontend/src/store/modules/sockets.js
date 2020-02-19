import Vue from 'vue'

const state = {
  isConnected: false,
  message: '',
  reconnectError: false
}

const getters = {
  isConnected: (state) => {
    return state.isConnected
  }
}

const actions = {
  checkConnected ({ state, dispatch }, deploymentId) {
    if (!state.isConnected) {
      console.log(1)
      dispatch('connect', deploymentId)
    }
  },
  connect ({ commit, rootGetters }, deploymentId) {
    console.log(2)
    const data = { accessToken: rootGetters['user/getAccessToken'] }
    if (deploymentId) {
      data.deploymentId = deploymentId
    }
    this._vm.$socket.client.emit('login', data)
    commit('connected')
    console.log(3)
  },
  socket_login ({ rootGetters, commit }) {
    console.log('Recieved login event')
    console.log(rootGetters['user/getAccessToken'])
    this._vm.$socket.client.emit('login', { accessToken: rootGetters['user/getAccessToken'], deploymentId: rootGetters['incidents/getDeploymentId'] })
    commit('connected')
  },
  socket_reconnect ({ dispatch }) {
    dispatch('socket_login')
  }
}

const mutations = {
  SOCKET_ONOPEN (state, event) {
    console.log(2324)
    Vue.prototype.$socket = event.currentTarget
    state.socket.isConnected = true
  },
  SOCKET_ONCLOSE (state, event) {
    state.isConnected = false
  },
  SOCKET_ONERROR (state, event) {
    console.error(state, event)
  },
  // default handler called for all methods
  SOCKET_ONMESSAGE (state, message) {
    state.message = message
  },
  // mutations for reconnect methods
  SOCKET_RECONNECT_ERROR (state) {
    state.reconnectError = true
  },
  connected (state) {
    state.isConnected = true
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
