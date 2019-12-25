import Vue from 'vue'
import App from './App.vue'
import store from './store'
import router from './router'
import VTooltip from 'v-tooltip'

import '@/assets/css/sb-admin-2.css'
import '@/assets/css/temp.css'

Vue.config.productionTip = false
Vue.use(require('vue-moment'))
Vue.use(VTooltip)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
