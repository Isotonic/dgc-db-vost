import Vue from 'vue'
import App from './App.vue'
import store from './store'
import router from './router'
import authInterceptor from './utils/authInterceptor'
import Axios from 'axios'
import VTooltip from 'v-tooltip'
import vueMoment from 'vue-moment'
import Vue2Filters from 'vue2-filters'
import skeleton from 'tb-skeleton'
import VueNoty from 'vuejs-noty'

import '@/assets/css/sb-admin-2.css'
import '@/assets/css/temp.css'
import 'tb-skeleton/dist/skeleton.css'
import 'vuejs-noty/dist/vuejs-noty.css'

Vue.config.productionTip = false
Vue.prototype.$http = Axios
Vue.use(VTooltip)
Vue.use(vueMoment)
Vue.use(Vue2Filters)
Vue.use(skeleton)

Vue.use(VueNoty, {
  timeout: 2000,
  progressBar: true
})

Vue.prototype.$http.defaults.baseURL = 'http://localhost:5000/api/'

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
