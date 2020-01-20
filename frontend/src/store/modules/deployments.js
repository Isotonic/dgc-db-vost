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
      .catch(error => {
        console.log(error.response.data.message)
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
