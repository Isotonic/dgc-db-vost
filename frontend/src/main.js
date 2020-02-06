import Vue from 'vue'
import App from './App.vue'
import store from './store'
import router from './router'
import authInterceptor from './utils/authInterceptor'
import { ApiMixin } from './utils/mixins'
import Axios from 'axios'
import VTooltip from 'v-tooltip'
import vueMoment from 'vue-moment'
import Vue2Filters from 'vue2-filters'
import VueNoty from 'vuejs-noty'
import TextareaAutosize from 'vue-textarea-autosize'
import { DropdownPlugin } from 'bootstrap-vue'

import '@/assets/css/sb-admin-2.css'
import '@/assets/css/temp.css'
import 'vuejs-noty/dist/vuejs-noty.css'

Vue.config.productionTip = false
Vue.prototype.$http = Axios
Vue.use(VTooltip)
Vue.use(vueMoment)
Vue.use(Vue2Filters)
Vue.use(TextareaAutosize)
Vue.use(DropdownPlugin)

Vue.use(VueNoty, {
  timeout: 2000,
  progressBar: true
})

Vue.filter('formatSize', function (size) {
  if (size > 1024 * 1024 * 1024 * 1024) {
    return (size / 1024 / 1024 / 1024 / 1024).toFixed(2) + ' TB'
  } else if (size > 1024 * 1024 * 1024) {
    return (size / 1024 / 1024 / 1024).toFixed(2) + ' GB'
  } else if (size > 1024 * 1024) {
    return (size / 1024 / 1024).toFixed(2) + ' MB'
  } else if (size > 1024) {
    return (size / 1024).toFixed(2) + ' KB'
  }
  return size.toString() + ' B'
})

Vue.mixin(ApiMixin)

Vue.prototype.$http.defaults.baseURL = process.env.NODE_ENV === 'development' ? 'http://localhost:5000/api/' : '/api/'

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
