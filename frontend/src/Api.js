import Vue from 'vue'

export default () => {
  return Vue.prototype.$http.create({
    withCredentials: false,
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }
  })
}
