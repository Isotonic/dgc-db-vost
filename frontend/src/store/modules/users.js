import Vue from 'vue'

const state = {
  users: [],
  deploymentId: null,
  loaded: false
}

const getters = {
  isLoaded: (state) => {
    return state.loaded
  },
  getUsers: (state) => {
    return state.users
  },
  getUsersGrouped: (state) => {
    let groups = {}
    let groupsArray = []
    for (let user of state.users) {
      const userGroup = user.group ? user.group.name : 'No Group'
      if (userGroup in groups) {
        groups[userGroup].push(user)
      } else {
        groups[userGroup] = [user]
      }
    }
    for (let group in groups) {
      groupsArray.push({ name: group, users: groups[group] })
    }
    return groupsArray
  }
}

const actions = {
  fetchUsers ({ state, commit, dispatch }, deploymentId) {
    return new Promise((resolve, reject) => {
      if ((state.deploymentId && state.deploymentId !== deploymentId) || (state.loaded && state.deploymentId === null)) {
        dispatch('storeDestroy')
      }
      if (!state.loaded) {
        commit('setDeploymentId', deploymentId)
        Vue.prototype.$api
          .get(`/deployments/${deploymentId}/users`)
          .then(r => r.data)
          .then(users => {
            commit('setUsers', users)
            commit('setLoaded', true)
            resolve()
          })
          .catch((error) => {
            reject(error)
          })
      } else {
        resolve()
      }
    })
  },
  refetch ({ state, commit }) {
    if (state.loaded) {
      Vue.prototype.$api
        .get(`/deployments/${state.deploymentId}/users`)
        .then(r => r.data)
        .then(users => {
          commit('setUsers', users)
        })
    }
  },
  storeDestroy ({ commit }) {
    commit('destroy')
  }
}

const mutations = {
  setUsers (state, value) {
    state.users = value
  },
  setDeploymentId (state, value) {
    state.deploymentId = value
  },
  setLoaded (state, value) {
    state.loaded = value
  },
  destroy (state) {
    state.users = []
    state.deploymentId = null
    state.loaded = false
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
