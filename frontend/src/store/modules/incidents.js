import Vue from 'vue'
import router from '@/router'

const state = {
  loaded: false,
  actionsRequiredLoaded: false,
  deploymentId: null,
  incidents: [],
  actionsRequired: []
}

const getters = {
  hasLoaded: (state) => {
    return state.loaded
  },
  hasActionsRequiredLoaded: (state) => {
    return state.actionsRequiredLoaded
  },
  getDeploymentId: (state) => {
    return state.deploymentId
  },
  getIncident: (state) => (id) => {
    return state.incidents.find(incident => incident.id === id)
  },
  getIncidents: (state) => {
    return state.incidents
  },
  getAssignedIncidents: (state, getters, rootState, rootGetters) => {
    const user = rootGetters['user/getUser']
    return state.incidents.filter(incident => incident.assignedTo.some(assignedTo => assignedTo.id === user.id))
  },
  getActionsRequired: (state) => {
    return state.actionsRequired
  },
  getActionsRequiredAmount: (state) => {
    return state.actionsRequired.length
  }
}

const actions = {
  checkLoaded ({ state, commit, dispatch }, deploymentId) {
    if ((state.deploymentId && state.deploymentId !== deploymentId) || (state.loaded && state.deploymentId === null)) {
      dispatch('storeDestroy')
    }
    if (!state.loaded) {
      commit('setDeploymentId', deploymentId)
      dispatch('fetchAll', deploymentId)
    }
  },
  fetchAll ({ commit }, deploymentId) {
    Vue.prototype.$api
      .get(`deployments/${deploymentId}/incidents`)
      .then(r => r.data)
      .then(incidents => {
        commit('setIncidents', incidents)
        commit('setLoaded', true)
      })
      .catch(_ => {
        router.push({ name: 'pageNotFound' })
      })
  },
  fetchActionsRequired ({ commit }, deploymentId) {
    if (deploymentId) {
      Vue.prototype.$api
        .get(`deployments/${deploymentId}/actions-required`)
        .then(r => r.data)
        .then(actionsRequired => {
          commit('setActionsRequired', actionsRequired)
          commit('setActionsRequiredLoaded', true)
        })
    }
  },
  refetch ({ state, commit, rootGetters }) {
    Vue.prototype.$api
      .get(`deployments/${state.deploymentId}/incidents`)
      .then(r => r.data)
      .then(incidents => {
        commit('setIncidents', incidents)
      })
    if (rootGetters['user/hasPermission']('supervisor')) {
      Vue.prototype.$api
        .get(`deployments/${state.deploymentId}/actions-required`)
        .then(r => r.data)
        .then(actionsRequired => {
          commit('setActionsRequired', actionsRequired)
        })
    }
  },
  storeDestroy ({ commit }) {
    commit('destroy')
  }
}

const mutations = {
  setLoaded (state, value) {
    state.loaded = value
  },
  setActionsRequiredLoaded (state, value) {
    state.actionsRequiredLoaded = value
  },
  setDeploymentId (state, id) {
    state.deploymentId = id
  },
  setIncidents (state, incidents) {
    state.incidents = incidents
  },
  setActionsRequired (state, actionsRequired) {
    state.actionsRequired = actionsRequired
  },
  SOCKET_INCIDENT_ACTIVITY (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.activity.push(data.activity)
    }
  },
  SOCKET_TASK_ACTIVITY (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.activity.push(data.activity)
      }
    }
  },
  SOCKET_NEW_INCIDENT (state, data) {
    state.incidents.push(data.incident)
  },
  SOCKET_NEW_COMMENT (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.comments.push(data.comment)
    }
  },
  SOCKET_NEW_TASK (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.tasks.push(data.task)
    }
  },
  SOCKET_NEW_TASK_COMMENT (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.comments.push(data.comment)
      }
    }
  },
  SOCKET_NEW_SUBTASK (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.subtasks.push(data.subtask)
      }
    }
  },
  SOCKET_NEW_ACTION_REQUIRED (state, data) {
    state.actionsRequired.push(data.action)
  },
  SOCKET_CHANGE_PIN (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.pinned = data.pinned
    }
  },
  SOCKET_CHANGE_INCIDENT_DETAILS (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.name = data.name
      incident.description = data.description
      incident.type = data.type
      incident.reportedVia = data.reportedVia
      incident.linkedIncidents = data.linkedIncidents
      incident.reference = data.reference
      incident.icon = data.icon
    }
  },
  SOCKET_CHANGE_INCIDENT_STATUS (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.open = data.open
    }
  },
  SOCKET_CHANGE_INCIDENT_ALLOCATION (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.assignedTo = data.assignedTo
    } else {
      this._vm.$socket.client.emit('get_incident', { incidentId: data.id })
    }
  },
  SOCKET_CHANGE_INCIDENT_PRIORITY (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.priority = data.priority
    }
  },
  SOCKET_CHANGE_INCIDENT_PUBLIC (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.public = data.public
      incident.publicName = data.publicName
      incident.publicDescription = data.publicDescription
    }
  },
  SOCKET_CHANGE_INCIDENT_LOCATION (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.location = data.location
    }
  },
  SOCKET_CHANGE_COMMENT_PUBLIC (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const comment = incident.comments.find(comment => comment.id === data.id)
      if (comment) {
        comment.public = data.public
      }
    }
  },
  SOCKET_CHANGE_COMMENT_TEXT (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const comment = incident.comments.find(comment => comment.id === data.id)
      if (comment) {
        comment.text = data.text
        comment.editedAt = data.editedAt * 1000
      }
    }
  },
  SOCKET_CHANGE_TASK_STATUS (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.completed = data.completed
        task.completedAt = data.timestamp
      }
    }
  },
  SOCKET_CHANGE_TASK_NAME (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.name = data.name
      }
    }
  },
  SOCKET_CHANGE_TASK_DESCRIPTION (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.description = data.description
      }
    }
  },
  SOCKET_CHANGE_TASK_TAGS (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.tags = data.tags
      }
    }
  },
  SOCKET_CHANGE_TASK_ASSIGNED (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.assignedTo = data.assignedTo
      }
    }
  },
  SOCKET_CHANGE_TASK_COMMENT_TEXT (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        const comment = task.comments.find(comment => comment.id === data.id)
        if (comment) {
          comment.text = data.text
          comment.editedAt = data.editedAt * 1000
        }
      }
    }
  },
  SOCKET_CHANGE_SUBTASK_STATUS (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        const subtask = task.subtasks.find(subtask => subtask.id === data.id)
        if (subtask) {
          subtask.completed = data.completed
          subtask.completedAt = data.timestamp
        }
      }
    }
  },
  SOCKET_CHANGE_SUBTASK_EDIT (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        const subtask = task.subtasks.find(subtask => subtask.id === data.id)
        if (subtask) {
          subtask.name = data.name
          subtask.assignedTo = data.assignedTo
        }
      }
    }
  },
  SOCKET_REMOVE_INCIDENT (state, data) {
    state.incidents = state.incidents.filter(incident => incident.id !== data.id)
  },
  SOCKET_DELETE_COMMENT (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      incident.comments = incident.comments.filter(comment => comment.id !== data.id)
    }
  },
  SOCKET_DELETE_TASK (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      incident.tasks = incident.tasks.filter(task => task.id !== data.id)
    }
  },
  SOCKET_DELETE_TASK_COMMENT (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        task.comments = task.comments.filter(task => task.id !== data.id)
      }
    }
  },
  SOCKET_DELETE_SUBTASK (state, data) {
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        task.subtasks = task.subtasks.filter(task => task.id !== data.id)
      }
    }
  },
  SOCKET_DELETE_ACTION_REQUIRED (state, data) {
    state.actionsRequired = state.actionsRequired.filter(action => action.id !== data.id)
  },
  destroy (state) {
    state.loaded = false
    state.deploymentId = null
    state.incidents = []
    state.hasActionsRequiredLoaded = false
    state.actionsRequired = []
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
