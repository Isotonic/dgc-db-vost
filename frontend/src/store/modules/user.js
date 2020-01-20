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
    return state.user.group && (state.user.group.permissions.includes('supervisor') || state.user.group.permissions.includes(permission))
  }
}

const actions = {
  checkLoaded ({ state, commit }) {
    if (!state.user) {
      Vue.prototype.$api
        .get('users/me')
        .then(r => r.data)
        .then(user => {
          commit('setUser', user)
        })
        .catch(response => {
          console.log(response.data.errors)
        })
    }
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
          resolve()
        })
        .catch(error => {
          console.log(error)
          reject(error)
        })
    })
  },
  authRefresh ({ state, commit, dispatch }) {
    return new Promise((resolve, reject) => {
      Vue.prototype.$http
        .get('auth/refresh-access', { headers: { 'Authorization': `Bearer ${state.refreshToken}` } })
        .then(r => r.data)
        .then(tokens => {
          console.log(tokens)
          commit('setAccessToken', tokens.access_token)
          commit('setRefreshToken', tokens.refresh_token)
          dispatch('checkLoaded')
          resolve()
        })
        .catch((error) => {
          console.log(error)
          reject(error)
        })
    })
  },
  authRequired ({ dispatch }) {
    const currentPath = window.location.pathname
    dispatch('storeDestroy')
    router.push({ name: 'login', query: { redirect: currentPath } })
  },
  logout ({ dispatch }) {
    dispatch('storeDestroy')
    router.push({ name: 'login' })
  },
  storeDestroy ({ commit, dispatch }) {
    commit('deleteAccessToken')
    commit('deleteRefreshToken')
    dispatch('deployments/destroy', null, { root: true })
    dispatch('incidents/destroy', null, { root: true })
  }
}

const mutations = {
  setAccessToken (state, value) {
    localStorage.setItem('accessToken', value)
    state.accessToken = value
    Vue.prototype.$api.defaults.headers['Authorization'] = `Bearer ${value}`
    console.log(Vue.prototype.$api.defaults.headers)
  },
  setRefreshToken (state, value) {
    localStorage.setItem('refreshToken', value)
    state.refreshToken = value
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
