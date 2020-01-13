<template>
  <div>
    <div id="wrapper">
    <sidebar :title="deployment.name" :deploymentId="deployment.id" :deploymentName="deployment.name"/>
      <div id="content-wrapper" class="d-flex flex-column">
          <topbar />
          <div class="container-fluid">
            <div class="d-sm-flex align-items-center justify-content-between mb-4">
                <h1 class="h3 mb-0">{{ deployment.name }}</h1>
                <button class="btn btn-icon-split btn-success mb-1" @click="isNewIncidentModalVisible = true">
                  <span class="btn-icon">
                  <i class="fas fa-plus"></i>
                  </span>
                  <span class="text">New Incident</span>
                </button>
                <NewIncidentModal v-show="isNewIncidentModalVisible" :visible="isNewIncidentModalVisible" @close="isNewIncidentModalVisible = false" />
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
            <div class="card-header py-3">
              <h6 class="m-0 font-weight-bold text-primary">Incidents</h6>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <div id="IncidentsTable">
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
import router from '@/router/index.js'
import { mapGetters, mapActions } from 'vuex'
import { ClientTable, Event } from 'vue-tables-2'

import Topbar from '@/components/Topbar.vue'
import Sidebar from '@/components/Sidebar.vue'
import NewIncidentModal from '@/components/modals/NewIncident.vue'

Vue.use(ClientTable)

export default {
  name: 'deployments',
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
      incidents: [
        { 'id': 1, 'pinned': true, 'name': 'Hmm', 'location': 'Test', 'priority': 'Standard', 'assigned_to': 'Idk', 'taskPercentage': 10, 'lastUpdated': '2019-12-12 10:08:08.033814' },
        { 'id': 2, 'pinned': true, 'name': 'DKSJD', 'location': 'EFSEF', 'priority': 'Standard', 'assignedTo': 'fESFS', 'taskPercentage': 60, 'lastUpdated': '2019-12-14 10:08:08.033814' },
        { 'id': 3, 'pinned': false, 'name': 'DKSJD', 'location': 'EFSEF', 'priority': 'Standard', 'assignedTo': 'fESFS', 'taskPercentage': 60, 'lastUpdated': '2019-12-14 10:08:08.033814' },
        { 'id': 1, 'pinned': false, 'name': 'Hmm', 'location': 'Test', 'priority': 'Standard', 'assigned_to': 'Idk', 'taskPercentage': 10, 'lastUpdated': '2019-12-12 10:08:08.033814' }
      ],
      incidentStat: { incidents: 12 },
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
          pinned: function (h, row, index) {
            return <i class={row.pinned ? 'fas fa-bookmark' : 'far fa-bookmark'}></i>
          },
          taskPercentage: function (h, row, index) {
            let bgClass = 'bg-danger'
            if (row.taskPercentage >= 80) {
              bgClass = 'bg-success'
            } else if (row.taskPercentage >= 50) {
              bgClass = 'bg-orange'
            } else if (row.taskPercentage >= 25) {
              bgClass = 'bg-warning'
            }
            return <span class={'badge text-light ' + bgClass}>{row.taskPercentage}%</span>
          },
          lastUpdated: function (h, row, index) {
            return this.$moment(row.lastUpdated).fromNow()
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
    ...mapActions('deployments', {
      checkLoaded: 'checkLoaded'
    })
  },
  computed: {
    ...mapGetters('deployments', {
      getDeployment: 'getDeployment'
    }),
    deployment: function () {
      return this.getDeployment(this.deploymentId)
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
    }
  },
  async created () {
    this.checkLoaded()
  },
  mounted () {
    let self = this
    Event.$on('vue-tables.row-click', function (data) {
      router.push({ name: 'incident', params: { deploymentName: self.deployment.name.replace(' ', '-'), deploymentId: self.deployment.id, incidentName: data.row.name.replace(' ', '-'), incidentId: data.row.id } })
    })
  }
}
</script>
