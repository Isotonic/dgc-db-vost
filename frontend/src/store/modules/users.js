import Vue from 'vue'

const state = {
  users: [],
  loaded: false
}

const getters = {
  isLoaded: (state) => {
    return state.loaded
  },
  getUsers: (state) => {
    return state.groups
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
  fetchUsers ({ commit }, deploymentId) {
    return new Promise((resolve, reject) => {
      Vue.prototype.$api
        .get(`/deployments/${deploymentId}/users`)
        .then(r => r.data)
        .then(users => {
          commit('setUsers', users)
          commit('setLoaded')
          resolve()
        })
        .catch((error) => {
          console.log(error)
          reject(error)
        })
    })
  },
  storeDestroy ({ commit }) {
    commit('destroy')
  }
}

const mutations = {
  setUsers (state, value) {
    state.users = value
  },
  setLoaded (state) {
    state.loaded = true
  },
  destroy (state) {
    state.users = []
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
