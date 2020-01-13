import Vue from 'vue'

const state = {
  loaded: false,
  deployments: []
}

const getters = {
  getAll: (state) => {
    return state.deployments
  },
  getDeployment: (state) => (id) => {
    return state.deployments.find(deployments => deployments.id === id)
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
    console.log(Vue.prototype.$api.defaults.headers.common['Authorization'])
    Vue.prototype.$api
      .get('deployments/list')
      .then(r => r.data)
      .then(deployments => {
        commit('setDeployments', deployments)
      })
  },
  destroy ({ commit }) {
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
