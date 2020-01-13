import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import deployments from './modules/deployments'
import incidents from './modules/incidents'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    user,
    deployments,
    incidents
  }
})
