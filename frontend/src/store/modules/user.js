import Vue from 'vue'
import router from '@/router'

const state = {
  user: null,
  accessToken: localStorage.getItem('accessToken') || '',
  refreshToken: localStorage.getItem('refreshToken') || ''
}

const getters = {
  loggedIn: (state) => {
    return state.accessToken !== ''
  },
  getAccessToken: (state) => {
    return state.accessToken
  },
  getUser: (state) => {
    return state.user
  },
  getName: (state) => {
    if (!state.user) {
      return ''
    }
    return `${state.user.firstname} ${state.user.surname}`
  },
  getAvatarUrl: (state) => {
    if (!state.user) {
      return ''
    }
    return state.user.avatarUrl
  },
  hasPermission: (state) => (permission) => {
    if (!state.user) {
      return false
    }
    return state.user.status > 1 || (state.user.group && (state.user.group.permissions.includes('supervisor') || state.user.group.permissions.includes(permission)))
  }
}

const actions = {
  checkLoaded ({ state, commit, dispatch }, deploymentId) {
    if (!state.user && localStorage.getItem('accessToken') !== null) {
      Vue.prototype.$api
        .get('users/me')
        .then(r => r.data)
        .then(user => {
          commit('setUser', user)
          if (deploymentId !== null) {
            dispatch('checkActionsRequired', deploymentId)
          }
        })
    } else if (deploymentId !== null) {
      dispatch('checkActionsRequired', deploymentId)
    }
  },
  checkActionsRequired ({ dispatch, getters, rootGetters }, deploymentId) {
    if (getters['hasPermission']('supervisor') && !rootGetters['incidents/hasActionsRequiredLoaded']) {
      dispatch('incidents/fetchActionsRequired', deploymentId, { root: true })
    }
  },
  refetch ({ commit }) {
    Vue.prototype.$api
      .get('users/me')
      .then(r => r.data)
      .then(user => {
        commit('setUser', user)
      })
  },
  login ({ commit, dispatch }, [email, password]) {
    return new Promise((resolve, reject) => {
      Vue.prototype.$http
        .post('auth/login', { email: email, password: password })
        .then(r => r.data)
        .then(tokens => {
          commit('setAccessToken', tokens.access_token)
          commit('setRefreshToken', tokens.refresh_token)
          dispatch('checkLoaded')
          localStorage.removeItem('showingIncidents')
          localStorage.removeItem('showingStatus')
          localStorage.removeItem('showingIncidentsMap')
          localStorage.removeItem('showingStatusMap')
          localStorage.removeItem('heatmapMap')
          localStorage.removeItem('sortedByTypeMap')
          localStorage.removeItem('sortedByOrderMap')
          localStorage.removeItem('minimiseSidebar')
          resolve()
        })
        .catch(error => {
          reject(error)
        })
    })
  },
  authRefresh ({ state, commit, dispatch, rootGetters }) {
    return new Promise((resolve, reject) => {
      Vue.prototype.$http
        .get('auth/refresh-access', { headers: { 'Authorization': `Bearer ${state.refreshToken}` } })
        .then(r => r.data)
        .then(tokens => {
          commit('setAccessToken', tokens.access_token)
          commit('setRefreshToken', tokens.refresh_token)
          dispatch('checkLoaded')
          if (!rootGetters['sockets/isConnected']) {
            dispatch('sockets/connect', null, { root: true })
          }
          resolve()
        })
        .catch((error) => {
          reject(error)
        })
    })
  },
  authRequired ({ dispatch }) {
    const currentPath = window.location.pathname
    dispatch('storeDestroy')
    router.push({ name: 'login', query: { redirect: currentPath } })
  },
  updateDetails ({ commit }, [firstname, surname, email]) {
    commit('updateFirstname', firstname)
    commit('updateSurname', surname)
    commit('updateEmail', email)
  },
  updateTokens ({ commit }, [accessToken, refreshToken]) {
    commit('setAccessToken', accessToken)
    commit('setRefreshToken', refreshToken)
  },
  socket_newNotification ({ commit }, data) {
    commit('addNewNotification', data)
    if (data.type === 'assigned_incident') {
      Vue.noty.success(`You have been assigned to ${data.incidentName}.`)
    } else if (data.type === 'unassigned_incident') {
      Vue.noty.error(`You have been unassigned from ${data.incidentName}.`)
    } else if (data.type === 'assigned_task') {
      Vue.noty.success(`You have been assigned to task ${data.taskName}.`)
    } else if (data.type === 'unassigned_task') {
      Vue.noty.error(`You have been unassigned from task ${data.taskName}.`)
    } else if (data.type === 'assigned_subtask') {
      Vue.noty.success(`You have been assigned to subtask ${data.subtaskName}.`)
    } else if (data.type === 'unassigned_subtask') {
      Vue.noty.error(`You have been unassigned from subtask ${data.subtaskName}.`)
    } else if (data.type === 'flagged_incident') {
      Vue.noty.error(`${data.triggeredBy.firstname} ${data.triggeredBy.surname} has flagged ${data.incidentName} with reason: ${data.reason}.`)
    }
  },
  logout ({ dispatch }) {
    dispatch('storeDestroy')
    this._vm.$socket.client.close()
    router.push({ name: 'publicMap' })
  },
  storeDestroy ({ commit, dispatch }) {
    commit('deleteAccessToken')
    commit('deleteRefreshToken')
    commit('deleteUser')
    dispatch('deployments/storeDestroy', null, { root: true })
    dispatch('incidents/storeDestroy', null, { root: true })
    dispatch('users/storeDestroy', null, { root: true })
    localStorage.removeItem('showingIncidents')
    localStorage.removeItem('showingStatus')
    localStorage.removeItem('showingIncidentsMap')
    localStorage.removeItem('showingStatusMap')
    localStorage.removeItem('heatmapMap')
    localStorage.removeItem('sortedByTypeMap')
    localStorage.removeItem('sortedByOrderMap')
    localStorage.removeItem('minimiseSidebar')
  }
}

const mutations = {
  setAccessToken (state, value) {
    localStorage.accessToken = value
    state.accessToken = value
    Vue.prototype.$api.defaults.headers['Authorization'] = `Bearer ${value}`
  },
  setRefreshToken (state, value) {
    localStorage.refreshToken = value
    state.refreshToken = value
  },
  updateFirstname (state, firstname) {
    state.user.firstname = firstname
  },
  updateSurname (state, surname) {
    state.user.surname = surname
  },
  updateEmail (state, email) {
    state.user.email = email
  },
  addNewNotification (state, notification) {
    state.user.notifications.push(notification)
  },
  SOCKET_CHANGE_USER_AVATAR (state, data) {
    state.user.avatarUrl = `${data.avatarUrl}?${new Date().getTime()}`
  },
  SOCKET_DELETE_NOTIFICATION (state, data) {
    state.user.notifications = state.user.notifications.filter(notification => notification.id !== data.id)
  },
  SOCKET_DELETE_ALL_NOTIFICATIONS (state) {
    state.user.notifications = []
  },
  deleteAccessToken (state) {
    localStorage.removeItem('accessToken')
    state.accessToken = ''
    delete Vue.prototype.$api.defaults.headers.common['Authorization']
  },
  deleteRefreshToken (state) {
    localStorage.removeItem('refreshToken')
    state.refreshToken = ''
  },
  deleteUser (state) {
    state.user = null
  },
  setUser (state, value) {
    state.user = value
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
