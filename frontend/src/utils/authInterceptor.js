// Credit to Emeke Ajeh
// https://gist.github.com/Godofbrowser/bf118322301af3fc334437c683887c5f

import store from '@/store'
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

const interceptor = (axiosInstance) => (error) => {
  const _axios = axiosInstance
  const originalRequest = error.config
  if (error.response.status === 401 && !originalRequest._retry) {
    if (isRefreshing) {
      return new Promise(function (resolve, reject) {
        failedQueue.push({ resolve, reject })
      })
        .then(token => {
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          return _axios.request(originalRequest)
        })
        .catch(err => {
          return Promise.reject(err)
        })
    }
    originalRequest._retry = true
    isRefreshing = true
    return new Promise((resolve, reject) => {
      store.dispatch('user/authRefresh')
        .then(() => {
          const token = store.getters['user/getAccessToken']
          originalRequest.headers['Authorization'] = `Bearer ${token}`
          processQueue(null, token)
          resolve(_axios(originalRequest))
        })
        .catch((err) => {
          processQueue(err, null)
          reject(err)
          store.dispatch('user/authRequired')
        })
        .then(() => {
          isRefreshing = false
        })
    })
  }

  return Promise.reject(error)
}

export default interceptor
