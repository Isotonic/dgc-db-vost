<template>
  <div id="wrapper">
    <sidebar :deploymentId="this.deploymentId" :deploymentName="deploymentNameApi" ref="sidebar" />
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :deploymentId="deploymentId" :deploymentName="deploymentNameApi" @toggleSidebar="toggleSidebar" />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 v-if="this.deployment" class="font-weight-bold mb-0">{{ this.deployment.name }}</h1>
        </div>
        <div class="row">
          <div class="col-xl-12">
            <div class="card">
              <div class="card-header d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Actions Required</h6>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <v-client-table id="ActionsRequiredTable" :data="actionsRequired" :columns="columns" :options="options">
                    <div slot="actions" slot-scope="{row}">
                      <i class="fas fa-check hover pl-4" v-tooltip="'Mark dealt with'" @click="markDealtWith(row, false)"></i>
                      <i v-if="isMarkComplete(row)" class="fas fa-check-double hover pl-4" v-tooltip="`Change to ${isMarkClosed(row) ? 'closed' : 'open'} and mark dealt with`" @click="markDealtWith(row, true)"></i>
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
import { Event } from 'vue-tables-2'
import { mapGetters, mapActions } from 'vuex'

import router from '@/router/index'
import Topbar from '@/components/Topbar'
import Sidebar from '@/components/Sidebar'

export default {
  name: 'actionsRequired',
  components: {
    Topbar,
    Sidebar
  },
  props: {
    deploymentName: String,
    deploymentId: Number
  },
  data () {
    return {
      showingIncidents: 'assigned',
      sortedBy: ['lastUpdatedAt', -1],
      columns: ['name', 'requestedBy', 'type', 'reason', 'requestedAt', 'actions'],
      options: {
        headings: {
          name: 'Incident Title',
          requestedBy: 'Requested By',
          type: 'Type',
          reason: 'Reason',
          requestedAt: 'Requested',
          actions: 'Actions'
        },
        templates: {
          name: function (h, row, index) {
            return row.incident.name
          },
          requestedBy: function (h, row, index) {
            return `${row.requestedBy.firstname} ${row.requestedBy.surname}`
          },
          reason: function (h, row, index) {
            return row.reason ? row.reason : 'N/A'
          },
          requestedAt: function (h, row, index) {
            return this.$moment.unix(row.requestedAt).fromNow()
          }
        },
        customSorting: {
          lastUpdated: function (ascending) {
            return function (a, b) {
              let lastA = a.requestedAt
              let lastB = b.requestedAt

              lastA = isNaN(lastA) ? -1 : lastA
              lastB = isNaN(lastB) ? -1 : lastB

              if (ascending) {
                return lastA >= lastB ? 1 : -1
              }
              return lastA <= lastB ? 1 : -1
            }
          }
        },
        filterAlgorithm: {
          requestedBy (row, query) {
            return (`${row.firstname} ${row.surname}`).toLowerCase().includes(query)
          }
        },
        orderBy: {
          column: 'requestedBy',
          ascending: true
        },
        summary: 'Table of actions required by a supervisor in the deployment',
        destroyEventBus: true,
        resizeableColumns: true,
        sortIcon: { base: 'float-right fas', up: 'fa-sort-up', down: 'fa-sort-down', is: 'fa-sort' },
        highlightMatches: true
      }
    }
  },
  methods: {
    isMarkComplete: function (row) {
      return row.type === 'Mark As Closed' || row.type === 'Mark As Open'
    },
    isMarkClosed: function (row) {
      return row.type === 'Mark As Closed'
    },
    markDealtWith: function (row, carryOutAction) {
      this.ApiPut(`actions-required/${row.id}`, { carryOutAction: carryOutAction })
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
    ...mapGetters('user', {
      hasPermission: 'hasPermission'
    }),
    ...mapGetters('deployments', {
      getDeployment: 'getDeployment'
    }),
    ...mapGetters('incidents', {
      hasLoaded: 'hasLoaded',
      hasActionsRequiredLoaded: 'hasActionsRequiredLoaded',
      getDeploymentId: 'getDeploymentId',
      getIncident: 'getIncident',
      actionsRequired: 'getActionsRequired'
    })
  },
  watch: {
    deployment: {
      deep: true,
      handler () {
        if (this.deployment && this.deploymentName !== this.deployment.name.replace(/ /g, '-')) {
          this.deploymentName = this.deployment.name
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(/ /g, '-')}-${this.deploymentId}/map`)
        }
      }
    }
  },
  async created () {
    this.checkUserLoaded(this.deploymentId)
    this.checkDeploymentsLoaded()
    this.checkIncidentsLoaded(this.deploymentId)
    this.checkSocketsConnected(this.deploymentId)
  },
  mounted () {
    let self = this
    Event.$on('vue-tables.row-click', function (data) {
      const sel = getSelection().toString()
      if (data.event.target.className.includes('fas') || sel) {
        return
      }
      router.push({ name: 'incident', params: { deploymentName: self.deploymentNameApi.replace(/ /g, '-'), deploymentId: self.deploymentId, incidentName: data.row.incident.name.replace(/ /g, '-'), incidentId: data.row.incident.id } })
    })
  }
}
</script>
