import Vue from 'vue'
import router from '@/router'

const state = {
  loaded: false,
  deploymentId: null,
  incidents: []
}

const getters = {
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
  }
}

const actions = {
  checkLoaded ({ state, commit, dispatch }, deploymentId) {
    if ((state.deploymentId && state.deploymentId !== deploymentId) || (state.loaded && !state.deploymentId)) {
      dispatch('destroy')
    }
    if (!state.loaded) {
      dispatch('fetchAll', deploymentId)
      commit('setLoaded', true)
    }
  },
  fetchAll ({ commit }, deploymentId) {
    console.log(Vue.prototype.$api.defaults.headers['Authorization'])
    Vue.prototype.$api
      .get(`deployments/${deploymentId}/incidents`)
      .then(r => r.data)
      .then(incidents => {
        commit('setDeployment', deploymentId)
        commit('setIncidents', incidents)
      })
      .catch(error => {
        console.log(error.response.data.message)
        router.push({ name: 'pageNotFound' })
      })
  },
  storeDestroy ({ commit }) {
    commit('destroy')
  }
}

const mutations = {
  setLoaded (state, value) {
    state.loaded = value
  },
  setDeployment (state, id) {
    state.deploymentId = id
  },
  setIncidents (state, incidents) {
    state.incidents = incidents
  },
  SOCKET_INCIDENT_ACTIVITY (state, data) {
    console.log('Recieved incident activity event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.activity.push(data.activity)
    }
  },
  SOCKET_NEW_INCIDENT (state, data) {
    console.log('Recieved incident event')
    state.incidents.push(data.incident)
  },
  SOCKET_TASK_ACTIVITY (state, data) {
    console.log('Recieved task activity event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.activity.push(data.activity)
      }
    }
  },
  SOCKET_NEW_COMMENT (state, data) {
    console.log('Recieved comment event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.comments.push(data.comment)
    }
  },
  SOCKET_NEW_TASK (state, data) {
    console.log('Recieved task event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.tasks.push(data.task)
    }
  },
  SOCKET_NEW_TASK_COMMENT (state, data) {
    console.log('Recieved task comment event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.comments.push(data.comment)
      }
    }
  },
  SOCKET_NEW_SUBTASK (state, data) {
    console.log('Recieved subtask event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.subtasks.push(data.subtask)
      }
    }
  },
  SOCKET_CHANGE_INCIDENT_DETAILS (state, data) {
    console.log('Recieved details event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.name = data.name
      incident.description = data.description
      incident.type = data.type
      incident.reportedVia = data.reportedVia
      incident.reference = data.reference
    }
  },
  SOCKET_CHANGE_INCIDENT_STATUS (state, data) {
    console.log('Recieved status event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.open = data.open
    }
  },
  SOCKET_CHANGE_INCIDENT_ALLOCATION (state, data) {
    console.log('Recieved allocated to event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.assignedTo = data.assignedTo
    }
  },
  SOCKET_CHANGE_INCIDENT_PRIORITY (state, data) {
    console.log('Recieved priority event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.priority = data.priority
    }
  },
  SOCKET_CHANGE_INCIDENT_PUBLIC (state, data) {
    console.log('Recieved public event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.public = data.public
      incident.publicName = data.publicName
      incident.publicDescription = data.publicDescription
    }
  },
  SOCKET_CHANGE_INCIDENT_LOCATION (state, data) {
    console.log('Recieved location event')
    const incident = state.incidents.find(incident => incident.id === data.id)
    if (incident) {
      incident.location = data.location
    }
  },
  SOCKET_CHANGE_COMMENT_PUBLIC (state, data) {
    console.log('Recieved comment public event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const comment = incident.comments.find(comment => comment.id === data.id)
      if (comment) {
        comment.public = data.public
      }
    }
  },
  SOCKET_CHANGE_COMMENT_TEXT (state, data) {
    console.log('Recieved comment text event')
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
    console.log('Recieved task status event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.completed = data.completed
        task.completedAt = data.timestamp
      }
    }
  },
  SOCKET_CHANGE_TASK_DESCRIPTION (state, data) {
    console.log('Recieved task description event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.description = data.description
      }
    }
  },
  SOCKET_CHANGE_TASK_TAGS (state, data) {
    console.log('Recieved task tags event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.tags = data.tags
      }
    }
  },
  SOCKET_CHANGE_TASK_ASSIGNED (state, data) {
    console.log('Recieved task assigned event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.id)
      if (task) {
        task.assignedTo = data.assignedTo
      }
    }
  },
  SOCKET_CHANGE_TASK_COMMENT_TEXT (state, data) {
    console.log('Recieved task comment event')
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
    console.log('Recieved task tags event')
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
    console.log('Recieved task edit event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      console.log(543)
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        console.log(45365)
        const subtask = task.subtasks.find(subtask => subtask.id === data.id)
        if (subtask) {
          console.log(435)
          subtask.name = data.name
          subtask.assignedTo = data.assignedTo
        }
      }
    }
  },
  SOCKET_DELETE_COMMENT (state, data) {
    console.log('Recieved comment delete event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      incident.comments = incident.comments.filter(comment => comment.id !== data.id)
    }
  },
  SOCKET_DELETE_TASK (state, data) {
    console.log('Recieved task delete event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      incident.tasks = incident.tasks.filter(task => task.id !== data.id)
    }
  },
  SOCKET_DELETE_TASK_COMMENT (state, data) {
    console.log('Recieved task comment delete event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        task.comments = task.comments.filter(task => task.id !== data.id)
      }
    }
  },
  SOCKET_DELETE_SUBTASK (state, data) {
    console.log('Recieved subtask delete event')
    const incident = state.incidents.find(incident => incident.id === data.incidentId)
    if (incident) {
      const task = incident.tasks.find(task => task.id === data.taskId)
      if (task) {
        task.subtasks = task.subtask.filter(task => task.id !== data.id)
      }
    }
  },
  destroy (state) {
    state.loaded = false
    state.deploymentId = null
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
