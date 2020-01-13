import Vue from 'vue'
import router from '@/router'
// import { cloneDeep } from 'lodash'

const state = {
  accessToken: localStorage.getItem('accessToken') || '',
  refreshToken: localStorage.getItem('refreshToken') || ''
}

const getters = {
  loggedIn: (state) => {
    return state.accessToken !== ''
  },
  getAccessToken: (state) => {
    return state.accessToken
  }
}

const actions = {
  login ({ commit }, [email, password]) {
    return new Promise((resolve, reject) => {
      Vue.prototype.$http
        .post('auth/login', { email: email, password: password })
        .then(r => r.data)
        .then(tokens => {
          commit('setAccessToken', tokens.access_token)
          commit('setRefreshToken', tokens.refresh_token)
          resolve(tokens)
        })
        .catch(error => {
          console.log(error)
          reject(error)
        })
    })
  },
  authRefresh ({ state, commit }) {
    return new Promise((resolve, reject) => {
      Vue.prototype.$http
        .get('auth/refresh-access', { headers: { 'Authorization': `Bearer ${state.refreshToken}` } })
        .then(r => r.data)
        .then(tokens => {
          console.log(tokens)
          commit('setAccessToken', tokens.access_token)
          commit('setRefreshToken', tokens.refresh_token)
          resolve(tokens)
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
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
