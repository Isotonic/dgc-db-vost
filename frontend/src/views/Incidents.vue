<template>
  <div>
    <div id="wrapper">
    <sidebar :deploymentId="this.deploymentId" :deploymentName="deploymentNameApi"/>
      <div id="content-wrapper" class="d-flex flex-column">
        <topbar :deploymentId="deploymentId" :deploymentName="deploymentNameApi" />
        <div class="container-fluid">
          <div class="d-sm-flex align-items-center justify-content-between mb-4">
            <h1 v-if="this.deployment" class="font-weight-bold mb-0">{{ this.deployment.name }}</h1>
            <button class="btn btn-icon-split btn-success mb-1" @click="isNewIncidentModalVisible = true">
              <span class="btn-icon">
              <i class="fas fa-plus"></i>
              </span>
              <span class="text">New Incident</span>
            </button>
            <new-incident-modal v-show="isNewIncidentModalVisible" :visible="isNewIncidentModalVisible" @close="isNewIncidentModalVisible = false" />
          </div>
          <div class="row">
            <div class="col-xl-3 col-md-6 mb-4">
              <div class="card border-left-primary shadow">
                <div class="card-body">
                  <div class="row no-gutters align-items-center">
                    <div class="col mr-2">
                      <div class="text-s font-weight-bold text-primary text-uppercase mb-1">Total Incidents</div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800">{{ incidents.length }}</div>
                    </div>
                    <div class="col-auto">
                      <div class="icon icon-shape bg-primary text-white rounded-circle shadow">
                        <i class="fas fa-1fourx fa-clone"></i>
                      </div>
                    </div>
                  </div>
                  <p class="mt-3 mb-0 text-muted">
                    <span :class="['mr-2', incidentStatText]"><i :class="['fa', incidentStatIcon]"></i> {{ incidentStat.incidents }}</span>
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
                      <div class="text-s font-weight-bold text-warning text-uppercase mb-1">Response Time</div>
                      <div class="h5 mb-0 font-weight-bold text-gray-800">WIP</div>
                    </div>
                    <div class="col-auto">
                      <div class="icon icon-shape bg-warning text-white rounded-circle shadow">
                        <i class="fas fa-1fourx fa-hourglass-end"></i>
                      </div>
                    </div>
                  </div>
                  <p class="mt-3 mb-0 text-muted">
                    <span class="text-warning mr-2"><i class="fa"></i> 0%</span>
                    <span class="text-nowrap">since last hour</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="card shadow mb-4">
            <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
              <h6 class="m-0 font-weight-bold text-primary">Incidents</h6>
              <select v-model="showing" class="custom-select custom-select-sm text-primary font-weight-bold">
                <option value="all">All Incidents</option>
                <option value="assigned">Assigned Incidents</option>
                <option value="open">Open Incidents</option>
                <option value="closed">Closed Incidents</option>
              </select>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <div>
                  <v-client-table :data="incidents" :columns="columns" :options="options">
                    <div slot="child_row" slot-scope="props">
                      {{ props.row.name }}
                    </div>
                  </v-client-table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import router from '@/router/index'
import { mapGetters, mapActions } from 'vuex'
import { ClientTable, Event } from 'vue-tables-2'

import Topbar from '@/components/Topbar'
import Sidebar from '@/components/Sidebar'
import assignedTo from '@/components/utils/TableAssignedTo'
import NewIncidentModal from '@/components/modals/NewIncident'

Vue.use(ClientTable)

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
      incidentStat: { incidents: 12 },
      showing: 'open',
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
          assignedTo,
          pinned: function (h, row, index) {
            return <i class={row.pinned ? 'fas fa-bookmark' : 'far fa-bookmark'}></i>
          },
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
          }
        },
        orderBy: {
          column: 'pinned',
          ascending: false
        },
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
      if (this.showing === 'open') {
        return this.getOpenIncidents
      } else if (this.showing === 'assigned') {
        return this.getAssignedIncidents
      } else if (this.showing === 'closed') {
        return this.getClosedIncidents
      } else {
        return this.getIncidents
      }
    },
    incidentStatText: function () {
      return {
        'text-success': this.incidentStat.incidents < 0,
        'text-primary': this.incidentStat.incidents === 0,
        'text-danger': this.incidentStat.incidents > 0
      }
    },
    incidentStatIcon: function () {
      return {
        'fa-plus': this.incidentStat.incidents < 0,
        'fa-down': this.incidentStat.incidents > 0
      }
    },
    ...mapGetters('deployments', {
      getDeployment: 'getDeployment'
    }),
    ...mapGetters('incidents', {
      getDeploymentId: 'getDeploymentId',
      getIncidents: 'getIncidents',
      getOpenIncidents: 'getOpenIncidents',
      getAssignedIncidents: 'getAssignedIncidents',
      getClosedIncidents: 'getClosedIncidents'
    })
  },
  watch: {
    deployment: {
      deep: true,
      handler () {
        if (this.deployment && this.deploymentName !== this.deployment.name) {
          this.deploymentName = this.deployment.name
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(' ', '-')}-${this.deploymentId}/incidents`)
        }
      }
    }
  },
  async created () {
    this.checkUserLoaded()
    this.checkDeploymentsLoaded()
    this.checkIncidentsLoaded(this.deploymentId)
  },
  mounted () {
    let self = this
    Event.$on('vue-tables.row-click', function (data) {
      router.push({ name: 'incident', params: { deploymentName: self.deployment.name.replace(' ', '-'), deploymentId: self.deployment.id, incidentName: data.row.name.replace(' ', '-'), incidentId: data.row.id } })
    })
  }
}
</script>
