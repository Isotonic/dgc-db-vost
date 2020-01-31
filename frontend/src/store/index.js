import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'
import users from './modules/users'
import deployments from './modules/deployments'
import incidents from './modules/incidents'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {
    user,
    users,
    deployments,
    incidents
  }
})
