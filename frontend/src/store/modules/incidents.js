import Vue from 'vue'
import router from '@/router'

const state = {
  loaded: false,
  deploymentId: null,
  incidents: []
}

const getters = {
  getDeploymentId: (state) => {
    return state.deploymentId
  },
  getIncident: (state) => (id) => {
    console.log(state.incidents.find(incident => incident.id === id))
    return state.incidents.find(incident => incident.id === id)
  },
  getIncidents: (state) => {
    return state.incidents
  },
  getOpenIncidents: (state) => {
    return state.incidents.filter(incident => incident.open)
  },
  getAssignedIncidents: (state, getters, rootState, rootGetters) => {
    const user = rootGetters['user/getUser']
    return state.incidents.filter(incident => incident.assignedTo.some(assignedTo => assignedTo.id === user.id))
  },
  getClosedIncidents: (state) => {
    return state.incidents.filter(incident => !incident.open)
  }
}

const actions = {
  checkLoaded ({ state, commit, dispatch }, deploymentId) {
    if ((state.deploymentId && state.deploymentId !== deploymentId) || (state.loaded && !state.deploymentId)) {
      dispatch('destroy')
    }
    if (!state.loaded) {
      dispatch('fetchAll', deploymentId)
      commit('setLoaded', true)
    }
  },
  fetchAll ({ commit }, deploymentId) {
    console.log(Vue.prototype.$api.defaults.headers['Authorization'])
    Vue.prototype.$api
      .get(`deployments/${deploymentId}/incidents`)
      .then(r => r.data)
      .then(incidents => {
        commit('setDeployment', deploymentId)
        commit('setIncidents', incidents)
      })
      .catch(error => {
        console.log(error.response.data.message)
        // Vue.noty.error(error.response.data.message)
        router.push({ name: 'pageNotFound' })
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
  setDeployment (state, id) {
    state.deploymentId = id
  },
  setIncidents (state, incidents) {
    state.incidents = incidents
  },
  destroy (state) {
    state.loaded = false
    state.deploymentId = null
    state.incidents = []
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
