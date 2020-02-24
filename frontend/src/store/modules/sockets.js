const state = {
  isConnected: false,
  needsRefetching: false,
  deploymentId: null
}

const getters = {
  isConnected: (state) => {
    return state.isConnected
  }
}

const actions = {
  checkConnected ({ state, commit, dispatch }, deploymentId) {
    if (!state.isConnected) {
      console.log(1)
      commit('setDeploymentId', deploymentId)
      dispatch('connect')
    } else if (state.deploymentId !== deploymentId) {
      console.log(`Leaving deployment ${state.deploymentId} websocket`)
      this._vm.$socket.client.emit('leave', { deploymentId: state.deploymentId })
      commit('setDeploymentId', deploymentId)
      if (state.deploymentId !== null) {
        console.log(`Joining deployment ${state.deploymentId} websocket`)
        this._vm.$socket.client.emit('join_deployment', { deploymentId: state.deploymentId })
      }
    }
  },
  connect ({ state, rootGetters }) {
    console.log(2)
    this._vm.$socket.client.emit('join', { accessToken: rootGetters['user/getAccessToken'], deploymentId: state.deploymentId })
  },
  socket_connected ({ state, commit, dispatch }) {
    if (state.needsRefetching) {
      dispatch('user/refetch', null, { root: true })
      dispatch('deployments/refetch', null, { root: true })
      dispatch('incidents/refetch', null, { root: true })
      dispatch('users/refetch', null, { root: true })
      commit('setNeedsRefetching', false)
    }
  },
  socket_reconnect ({ commit, dispatch }) {
    commit('setConnected', false)
    console.log('Reconnecting')
    commit('setNeedsRefetching', true)
    dispatch('connect')
  },
  storeDestroy ({ commit }) {
    commit('destroy')
  }
}

const mutations = {
  setConnected (state, value) {
    state.isConnected = value
  },
  setNeedsRefetching (state, value) {
    state.needsRefetching = value
  },
  setDeploymentId (state, value) {
    state.deploymentId = value
  },
  SOCKET_CONNECTED (state) {
    console.log('Connected to websocket')
    state.isConnected = true
  },
  destroy (state) {
    state.isConnected = false
    state.deploymentId = false
    state.needsRefetching = false
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
