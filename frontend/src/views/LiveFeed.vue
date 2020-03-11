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
            <div class="card mb-5">
              <div class="card-header bg-white d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Live Feed</h6>
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
                  <activity-filter @changeFilter="changeFilter" />
                  <select v-model="sortBy" class="custom-select custom-select-sm text-primary font-weight-bold ml-2">
                    <option :value="1">Ascending</option>
                    <option :value="-1">Descending</option>
                  </select>
                </div>
              </div>
              <div class="card-body bg-light">
                <vcl-bullet-list v-if="!hasLoaded" :rows="4" />
                <ul v-else-if="this.activities.length" class="activity">
                  <live-feed-activity v-for="action in orderBy(activities, 'occurredAt', sortBy).slice((this.pageNum - 1) * 20, this.pageNum * 20)" :key="action.id" :action="action" :deploymentName="deploymentNameApi" :deploymentId="deploymentId" @userModal="openUserModal" />
                </ul>
                <h5 v-else class="font-weight-bold text-center mt-3">No activity.</h5>
                <div v-if="activities.length > 20" class="text-center">
                  <paginate :page-count="Math.ceil(activities.length/20)" :click-handler="changePage" :prev-text="'Prev'" :next-text="'Next'" :page-range="5" :container-class="'pagination'" />
                </div>
              </div>
              <user-modal v-if="isUserModalVisible" v-show="isUserModalVisible" :visible="isUserModalVisible" :deploymentName="deploymentName" :deploymentId="deploymentId" :userProp="userModal" @close="isUserModalVisible = false" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue2Filters from 'vue2-filters'
import Paginate from 'vuejs-paginate'
import { mapGetters, mapActions } from 'vuex'
import { VclBulletList } from 'vue-content-loading'

import Topbar from '@/components/Topbar'
import Sidebar from '@/components/Sidebar'
import LiveFeedActivity from '@/components/LiveFeedActivity'
import ActivityFilter from '@/components/utils/ActivityFilter'
import UserModal from '@/components/modals/User'

export default {
  name: 'incidentMap',
  mixins: [Vue2Filters.mixin],
  components: {
    Topbar,
    Sidebar,
    LiveFeedActivity,
    ActivityFilter,
    UserModal,
    Paginate,
    VclBulletList
  },
  props: {
    deploymentName: String,
    deploymentId: Number
  },
  data () {
    return {
      showingIncidents: 'all',
      showingStatus: 'open',
      filterActivities: 'all',
      userModal: null,
      isUserModalVisible: false,
      sortBy: -1,
      pageNum: 1
    }
  },
  methods: {
    changeFilter: function (value) {
      this.filterActivities = value
    },
    changePage: function (pageNum) {
      this.pageNum = pageNum
    },
    openUserModal (user) {
      this.userModal = user
      this.isUserModalVisible = true
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
      let incidents = []
      if (this.showingIncidents === 'assigned') {
        incidents = this.getAssignedIncidents
      } else {
        incidents = this.getIncidents
      }

      if (this.showingStatus === 'open') {
        return incidents.filter(incident => incident.open)
      } else if (this.showingStatus === 'closed') {
        return incidents.filter(incident => !incident.open)
      } else {
        return incidents
      }
    },
    activities: function () {
      const activities = this.incidents.flatMap(incident => incident.activity.map(activity => Object.assign({}, activity, { incidentName: incident.name, incidentId: incident.id, description: incident.description, priority: incident.priority, location: incident.location.properties.address, tasks: incident.tasks.length ? `${incident.tasks.filter(task => task.completedAt).length}/${incident.tasks.length}` : null, comments: incident.comments ? incident.comments.length : null })))
      if (this.filterActivities !== 'all') {
        return activities.filter(activity => activity.type === this.filterActivities)
      } else {
        return activities
      }
    },
    ...mapGetters('user', {
      hasPermission: 'hasPermission'
    }),
    ...mapGetters('deployments', {
      getDeployment: 'getDeployment'
    }),
    ...mapGetters('incidents', {
      hasLoaded: 'hasLoaded',
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
  }
}
</script>
