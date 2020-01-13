import Vue from 'vue'
import App from './App.vue'
import store from './store'
import router from './router'
import authInterceptor from './utils/authInterceptor'
import vueMoment from 'vue-moment'
import VTooltip from 'v-tooltip'
import Axios from 'axios'

import '@/assets/css/sb-admin-2.css'
import '@/assets/css/temp.css'

Vue.config.productionTip = false
Vue.prototype.$http = Axios
Vue.use(vueMoment)
Vue.use(VTooltip)

Vue.prototype.$http.defaults.baseURL = '/api/'

Vue.prototype.$api = Vue.prototype.$http.create({
  withCredentials: false,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${store.getters['user/getAccessToken']}`
  }
})

Vue.prototype.$api.interceptors.response.use(undefined, authInterceptor(Vue.prototype.$api))

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
