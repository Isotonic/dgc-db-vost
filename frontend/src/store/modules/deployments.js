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
  fetchDeployment ({ commit }, deploymentId) {
    Vue.prototype.$api
      .get(`deployments/${deploymentId}`)
      .then(r => r.data)
      .then(deployment => {
        commit('newDeployment', deployment)
      })
  },
  fetchAll ({ commit }) {
    Vue.prototype.$api
      .get('deployments')
      .then(r => r.data)
      .then(deployments => {
        commit('setDeployments', deployments)
      })
  },
  socket_newDeployment ({ commit, rootGetters }, data) {
    const user = rootGetters['user/getUser']
    const groupId = user.group ? user.group.id : null
    if ((!data.deployment.groups.length && !data.deployment.users.length) || (data.deployment.groups.some(deploymentGroup => deploymentGroup.id === groupId) || data.deployment.users.some(deploymentUser => deploymentUser.id === user.id) || rootGetters['user/hasPermission']('supervisor'))) {
      commit('newDeployment', data.deployment)
    }
  },
  socket_editDeployment ({ commit, rootGetters }, data) {
    const user = rootGetters['user/getUser']
    const groupId = user.group ? user.group.id : null
    const whitelisted = (!data.deployment.groups.length && !data.deployment.users.length) || (data.deployment.groups.some(deploymentGroup => deploymentGroup.id === groupId) || data.deployment.users.some(deploymentUser => deploymentUser.id === user.id) || rootGetters['user/hasPermission']('supervisor'))
    if (!state.deployments.some(deployment => deployment.id === data.deployment.id) && whitelisted) {
      commit('newDeployment', data.deployment)
    } else if (state.deployments.some(deployment => deployment.id === data.deployment.id) && !whitelisted) {
      commit('removeDeployment', data.deployment)
    } else {
      commit('editDeployment', data.deployment)
    }
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
  newDeployment (state, deployment) {
    state.deployments.push(deployment)
  },
  removeDeployment (state, dataDeployment) {
    state.deployments = state.deployments.filter(deployment => deployment.id !== dataDeployment.id)
  },
  editDeployment (state, dataDeployment) {
    const deployment = state.deployments.find(deployment => deployment.id === dataDeployment.id)
    deployment.name = dataDeployment.name
    deployment.description = dataDeployment.description
    deployment.open = dataDeployment.open
    deployment.reference = dataDeployment.groups
    deployment.users = dataDeployment.users
    deployment.groups = dataDeployment.groups
    deployment.closedAt = dataDeployment.closedAt
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
