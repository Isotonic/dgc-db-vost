
const state = {
  incidents: []
}

const getters = {

}

const actions = {
  destroy ({ commit }) {
    commit('destroy')
  }
}

const mutations = {
  destroy (state) {
    state.incidents = []
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
