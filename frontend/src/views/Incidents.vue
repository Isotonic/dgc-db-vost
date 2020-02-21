<template>
  <div id="wrapper">
  <sidebar :deploymentId="this.deploymentId" :deploymentName="deploymentNameApi" ref="sidebar" />
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :deploymentId="deploymentId" :deploymentName="deploymentNameApi" @toggleSidebar="toggleSidebar" />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 v-if="this.deployment" class="font-weight-bold mb-0">{{ this.deployment.name }}</h1>
          <button class="btn btn-icon-split btn-success mb-1" @click="isNewIncidentModalVisible = true">
            <span class="btn-icon">
            <i class="fas fa-plus"></i>
            </span>
            <span class="text">New Incident</span>
          </button>
          <new-incident-modal v-if="isNewIncidentModalVisible" v-show="isNewIncidentModalVisible" :visible="isNewIncidentModalVisible" :deploymentName="this.deploymentName" :deploymentId="this.deploymentId" @close="isNewIncidentModalVisible = false" />
        </div>
        <div class="row">
          <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-primary shadow">
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div class="text-s font-weight-bold text-primary text-uppercase mb-1">Total Incidents</div>
                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{ getShowingIncidents.length }}</div>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-primary text-white rounded-circle shadow">
                      <i class="fas fa-1fourx fa-clone"></i>
                    </div>
                  </div>
                </div>
                <p class="mt-2 mb-0 text-muted">
                  <span :class="['mr-2', totalIncidentsStat.class]"><i :class="['fa', 'fa-sm', totalIncidentsStat.icon]"></i>{{ totalIncidentsStat.stat }}</span>
                  <span class="text-nowrap">since last hour</span>
                </p>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-warning shadow">
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div class="text-s font-weight-bold text-warning text-uppercase mb-1">Avg. Response Time</div>
                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{ responseTimeStat }}</div>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-warning text-white rounded-circle shadow">
                      <i class="fas fa-1fourx fa-hourglass-end"></i>
                    </div>
                  </div>
                </div>
                <p class="mt-2 mb-0 text-muted">
                  <span :class="['mr-2', responseTimeBottomStat.class]"><i :class="['fa', 'fa-sm', responseTimeBottomStat.icon]"></i>{{ responseTimeBottomStat.stat }}%</span>
                  <span class="text-nowrap">since last hour</span>
                </p>
              </div>
            </div>
          </div>
        </div>
        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Incidents</h6>
            <div>
              <select v-if="hasPermission('view_all_incidents')" v-model="showingIncidents" class="custom-select custom-select-sm text-primary font-weight-bold">
                <option value="all">All Incidents</option>
                <option value="assigned">Assigned Incidents</option>
              </select>
              <select v-model="showingStatus" class="custom-select custom-select-sm text-primary font-weight-bold ml-2">
                <option value="open">Open Only</option>
                <option value="closed">Closed Only</option>
                <option value="both">Open and Closed</option>
              </select>
            </div>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <v-client-table id="IncidentsTable" :data="incidents" :columns="columns" :options="options" ref="incidentsTable">
                <div slot="child_row" slot-scope="props">
                  <span class="font-weight-bold">Description:</span> {{ props.row.description }}
                </div>
                <div slot="pinned" slot-scope="{row}">
                  <i :class="[row.pinned ? 'fas fa-bookmark' : 'far fa-bookmark']" v-tooltip="row.pinned ? 'Pinned' : 'Not pinned'" @click="changePin(row)"></i>
                </div>
                <div v-if="showingStatus !== 'both'" slot="name" slot-scope="{row}">
                  <span>{{ row.name }}</span>
                </div>
                <div v-else slot="name" slot-scope="{row}">
                  <span class="badge badge-dot">
                    <i :class="[row.open ? 'bg-success' : 'bg-info']" v-tooltip="row.open ? 'Open' : 'Closed'"></i>
                  </span>
                  {{row.name}}
                </div>
                <div slot="assignedTo" slot-scope="{row}">
                  <div v-if="row.assignedTo.length" class="avatar-group">
                    <i v-for="user in row.assignedTo" :key="user.id" class="avatar avatar-sm" v-tooltip="`${user.firstname} ${user.surname}`">
                      <img alt="Avatar" :src="user.avatarUrl" class="rounded-circle avatar-sm">
                    </i>
                  </div>
                  <div v-else>
                    Unassigned
                  </div>
                </div>
              </v-client-table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>

import { Event } from 'vue-tables-2'
import { mapGetters, mapActions } from 'vuex'

import router from '@/router/index'
import Topbar from '@/components/Topbar'
import Sidebar from '@/components/Sidebar'
import NewIncidentModal from '@/components/modals/NewIncident'

export default {
  name: 'incidents',
  components: {
    Topbar,
    Sidebar,
    NewIncidentModal
  },
  props: {
    deploymentName: String,
    deploymentId: Number
  },
  data () {
    return {
      showingIncidents: 'assigned',
      showingStatus: 'open',
      columns: ['pinned', 'name', 'location', 'priority', 'assignedTo', 'taskPercentage', 'lastUpdated'],
      options: {
        headings: {
          pinned: 'Pinned',
          name: 'Incident Title',
          location: 'Location',
          priority: 'Priority',
          assignedTo: 'Assigned To',
          taskPercentage: 'Tasks',
          lastUpdated: 'Last Updated'
        },
        templates: {
          location: function (h, row, index) {
            return <span class='font-smaller'>{row.location.properties.address}</span>
          },
          priority: function (h, row, index) {
            return <span class="badge badge-dot mr-4">
              <i class={'bg-' + row.priority} v-tooltip={row.priority + ' Priority'}></i> {row.priority}
            </span>
          },
          taskPercentage: function (h, row, index) {
            let bgClass = 'bg-danger'
            if (!row.tasks.length) {
              return 'None'
            }
            const taskPercentage = Math.round((row.tasks.filter(task => task.completed).length / row.tasks.length) * 100)
            if (taskPercentage >= 80) {
              bgClass = 'bg-success'
            } else if (taskPercentage >= 50) {
              bgClass = 'bg-orange'
            } else if (taskPercentage >= 25) {
              bgClass = 'bg-warning'
            }
            return <span class={'badge text-light ' + bgClass}>{taskPercentage}%</span>
          },
          lastUpdated: function (h, row, index) {
            return this.$moment.unix(row.lastUpdatedAt).fromNow()
          }
        },
        customSorting: {
          pinned: function (ascending) {
            return function (a, b) {
              let lastA = a.pinned
              let lastB = b.pinned

              if (lastA === lastB) {
                lastA = a.lastUpdatedAt
                lastB = b.lastUpdatedAt
              }
              if (ascending) {
                return lastA >= lastB ? 1 : -1
              }
              return lastA <= lastB ? 1 : -1
            }
          },
          assignedTo: function (ascending) {
            return function (a, b) {
              let lastA = a.assignedTo.length
              let lastB = b.assignedTo.length

              if (lastA === lastB) {
                lastA = a.lastUpdated
                lastB = b.lastUpdated
              }
              if (ascending) {
                return lastA >= lastB ? 1 : -1
              }
              return lastA <= lastB ? 1 : -1
            }
          },
          taskPercentage: function (ascending) {
            return function (a, b) {
              let lastA = Math.round((a.tasks.filter(task => task.completed).length / a.tasks.length) * 100)
              let lastB = Math.round((b.tasks.filter(task => task.completed).length / b.tasks.length) * 100)

              lastA = isNaN(lastA) ? -1 : lastA
              lastB = isNaN(lastB) ? -1 : lastB

              if (lastA === lastB) {
                lastA = a.lastUpdated
                lastB = b.lastUpdated
              }
              if (ascending) {
                return lastA >= lastB ? 1 : -1
              }
              return lastA <= lastB ? 1 : -1
            }
          },
          lastUpdated: function (ascending) {
            return function (a, b) {
              let lastA = a.lastUpdatedAt
              let lastB = b.lastUpdatedAt

              lastA = isNaN(lastA) ? -1 : lastA
              lastB = isNaN(lastB) ? -1 : lastB

              if (lastA === lastB) {
                lastA = a.pinned
                lastB = b.pinned
              }
              if (ascending) {
                return lastA >= lastB ? 1 : -1
              }
              return lastA <= lastB ? 1 : -1
            }
          }
        },
        filterAlgorithm: {
          assignedTo (row, query) {
            return (row.assignedTo.map(user => `${user.firstname} ${user.surname}`).join(' ')).toLowerCase().includes(query)
          }
        },
        orderBy: {
          column: 'pinned',
          ascending: false
        },
        summary: 'Table of incidents in deployment',
        destroyEventBus: true,
        resizeableColumns: true,
        sortIcon: { base: 'float-right fas', up: 'fa-sort-up', down: 'fa-sort-down', is: 'fa-sort' },
        highlightMatches: true,
        multiSorting: {
          pinned: [{
            column: 'lastUpdated',
            matchDir: true
          },
          {
            column: 'name',
            matchDir: false
          }
          ]
        }
      },
      isNewIncidentModalVisible: false
    }
  },
  methods: {
    calcResponseTime: function (closedIncidents) {
      let closedTime = 0
      for (let incident of closedIncidents) {
        closedTime += incident.closedAt - incident.createdAt
      }
      return closedTime / closedIncidents.length
    },
    changePin: function (incident) {
      this.ApiPost(`incidents/${incident.id}/pinned`, { pinned: !incident.pinned })
    },
    toggleSidebar: function () {
      this.$refs.sidebar.toggleSidebar()
    },
    ...mapActions('sockets', {
      checkSocketsConnected: 'checkConnected'
    }),
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    }),
    ...mapActions('deployments', {
      checkDeploymentsLoaded: 'checkLoaded'
    }),
    ...mapActions('incidents', {
      checkIncidentsLoaded: 'checkLoaded'
    })
  },
  computed: {
    deployment: function () {
      return this.getDeployment(this.deploymentId)
    },
    deploymentNameApi: function () {
      if (this.deployment) {
        return this.deployment.name
      }
      return this.deploymentName
    },
    incidents: function () {
      const incidents = this.getShowingIncidents
      if (this.showingStatus === 'open') {
        return incidents.filter(incident => incident.open)
      } else if (this.showingStatus === 'closed') {
        return incidents.filter(incident => !incident.open)
      } else {
        return incidents
      }
    },
    getShowingIncidents: function () {
      if (this.showingIncidents === 'assigned') {
        return this.getAssignedIncidents
      } else {
        return this.getIncidents
      }
    },
    totalIncidentsStat: function () {
      const hourAgo = (Date.now() / 1000) - 3600
      const twoHoursAgo = hourAgo - 3600
      const hourAgoIncidents = this.getShowingIncidents.filter(incident => incident.createdAt >= hourAgo).length
      const twoHoursAgoIncidents = this.getShowingIncidents.filter(incident => incident.createdAt >= twoHoursAgo && incident.createdAt < hourAgo).length
      if (hourAgoIncidents > twoHoursAgoIncidents) {
        return { stat: hourAgoIncidents - twoHoursAgoIncidents, class: 'text-danger', icon: 'fa-plus' }
      } else if (twoHoursAgoIncidents > hourAgoIncidents) {
        return { stat: twoHoursAgoIncidents - hourAgoIncidents, class: 'text-success', icon: 'fa-minus' }
      } else {
        return { stat: 0, class: 'text-primary', icon: '' }
      }
    },
    responseTimeStat: function () {
      const closedIncidents = this.getShowingIncidents.filter(incident => !incident.open)
      if (!closedIncidents.length) {
        return 0
      }
      const responseTime = this.calcResponseTime(closedIncidents)
      if (responseTime >= 86400) {
        return `${Math.floor(responseTime / 86400)}d ${this.$moment.unix(responseTime).format('hh[h] mm[m] ss[s]')}`
      } else if (responseTime >= 3600) {
        return this.$moment.unix(responseTime).format('hh[h] mm[m] ss[s]')
      } else if (responseTime >= 60) {
        return this.$moment.unix(responseTime).format('mm[m] ss[s]')
      } else {
        return this.$moment.unix(responseTime).format('mm[m] ss[s]')
      }
    },
    responseTimeBottomStat: function () {
      const hourAgo = (Date.now() / 1000) - 3600
      const nowIncidents = this.getShowingIncidents.filter(incident => !incident.open)
      const hourAgoIncidents = nowIncidents.filter(incident => incident.closedAt < hourAgo)
      if (!nowIncidents.length || !hourAgoIncidents.length) {
        return { stat: 0, class: 'text-warning', icon: '' }
      }
      const nowTime = this.calcResponseTime(nowIncidents)
      const hourAgoTime = this.calcResponseTime(hourAgoIncidents)

      if (nowTime > hourAgoTime) {
        return { stat: Math.round((nowTime / hourAgoTime) * 100), class: 'text-danger', icon: 'fa-plus' }
      } else if (hourAgoTime > nowTime) {
        return { stat: Math.round((hourAgoTime / nowTime) * 100), class: 'text-success', icon: 'fa-down' }
      } else {
        return { stat: 0, class: 'text-warning', icon: '' }
      }
    },
    ...mapGetters('user', {
      hasPermission: 'hasPermission'
    }),
    ...mapGetters('deployments', {
      getDeployment: 'getDeployment'
    }),
    ...mapGetters('incidents', {
      getDeploymentId: 'getDeploymentId',
      getIncidents: 'getIncidents',
      getAssignedIncidents: 'getAssignedIncidents'
    })
  },
  watch: {
    deployment: {
      deep: true,
      handler () {
        if (this.deployment && this.deploymentName !== this.deployment.name.replace(/ /g, '-')) {
          this.deploymentName = this.deployment.name
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(/ /g, '-')}-${this.deploymentId}/incidents`)
        }
      }
    },
    showingIncidents (value) {
      localStorage.showingIncidents = value
      this.$refs.incidentsTable.setPage(1)
    },
    showingStatus (value) {
      localStorage.showingStatus = value
    }
  },
  async created () {
    if (localStorage.showingIncidents) {
      this.showingIncidents = localStorage.showingIncidents
    }
    if (localStorage.showingStatus) {
      this.showingStatus = localStorage.showingStatus
    }
    this.checkUserLoaded(this.deploymentId)
    this.checkDeploymentsLoaded()
    this.checkIncidentsLoaded(this.deploymentId)
    this.checkSocketsConnected(this.deploymentId)
  },
  mounted () {
    let self = this
    Event.$on('vue-tables.row-click', function (data) {
      const sel = getSelection().toString()
      if (data.event.target.className.includes('fa-bookmark') || sel) {
        return
      }
      router.push({ name: 'incident', params: { deploymentName: self.deploymentNameApi.replace(/ /g, '-'), deploymentId: self.deploymentId, incidentName: data.row.name.replace(/ /g, '-'), incidentId: data.row.id } })
    })
  }
}
</script>
