import Vue from 'vue'

const state = {
  loaded: false,
  deployments: []
}

const getters = {
  getDeployment: (state) => (id) => {
    return state.deployments.find(deployment => deployment.id === id)
  },
  getAll: (state) => {
    return state.deployments
  },
  getUsers: (state) => {
    return state.deployments.users
  }
}

const actions = {
  checkLoaded ({ state, commit, dispatch }) {
    if (!state.loaded) {
      dispatch('fetchAll')
      commit('setLoaded', true)
    }
  },
  fetchAll ({ commit }) {
    Vue.prototype.$api
      .get('deployments')
      .then(r => r.data)
      .then(deployments => {
        commit('setDeployments', deployments)
      })
  },
  refetch ({ commit }) {
    Vue.prototype.$api
      .get('deployments')
      .then(r => r.data)
      .then(deployments => {
        commit('setDeployments', deployments)
      })
  },
  storeDestroy ({ commit }) {
    commit('destroy')
  }
}

const mutations = {
  setLoaded (state, value) {
    state.loaded = value
  },
  setDeployments (state, deployments) {
    state.deployments = deployments
  },
  SOCKET_NEW_DEPLOYMENT (state, data) {
    state.deployments.push(data.deployment)
  },
  SOCKET_CHANGE_DEPLOYMENT_EDIT (state, data) {
    const deployment = state.deployments.find(deployment => deployment.id === data.id)
    if (deployment) {
      deployment.name = data.name
      deployment.description = data.description
      deployment.open = data.open
      deployment.reference = data.groups
      deployment.users = data.users
      deployment.closedAt = data.closedAt
    }
  },
  destroy (state) {
    state.loaded = false
    state.deployments = []
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
