import Vue from 'vue'
const baseURL = 'http://localhost:5000/api/'

export default () => {
  return Vue.prototype.$http.create({
    baseURL: baseURL,
    withCredentials: false,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
}
