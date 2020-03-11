<template>
  <modal :title="'User'" :bigger="true" :bgLight="true" @close="close">
    <div>
      <img alt="Avatar" :src="user.avatarUrl" class="rounded-circle avatar">
      <span class="h4 font-weight-bold ml-4">{{ user.firstname }} {{ user.surname }}{{ user.group ? ' - ' + user.group.name : '' }}</span>
    </div>
    <hr />
    <h5 class="font-weight-bold mb-3">Assigned Incidents</h5>
    <div v-if="assignedIncidents.length">
      <a v-for="incident in orderBy(assignedIncidents, 'createdAt', 1)" :key="incident.id" class="text-primary" v-tooltip="{ content: incidentTooltip(incident), html: true }" @click="goToIncident(incident)">{{ incident.name }}{{ incident.id === currentIncidentId ? ' (Current Incident)' : '' }}<br /></a>
    </div>
    <p v-else class="card-text font-weight-bold text-center my-3">No assigned incidents currently.</p>
    <div>
    <hr />
      <span class="h5 font-weight-bold">Recent Activity</span>
      <activity-filter class="float-right" :current="filterActivities" :textBlack="true" @changeFilter="changeFilter" />
    </div>
    <div v-if="recentActivity.length">
      <ul class="activity mt-4">
        <live-feed-activity v-for="action in orderBy(recentActivity, 'occurredAt', -1).slice((this.pageNum - 1) * 5, this.pageNum * 5)" :key="action.id" :action="action" :deploymentName="deploymentName" :deploymentId="deploymentId" @userModal="changeUser" @close="close" />
      </ul>
      <div v-if="recentActivity.length > 5" class="text-center">
        <paginate :page-count="Math.ceil(recentActivity.length/5)" :click-handler="changePage" :prev-text="'Prev'" :next-text="'Next'" :page-range="5" :container-class="'pagination'" />
      </div>
    </div>
    <p v-else class="card-text font-weight-bold text-center my-3">No activity currently.</p>
  </modal>
</template>

<script>
import Vue2Filters from 'vue2-filters'
import Paginate from 'vuejs-paginate'
import { mapGetters, mapActions } from 'vuex'

import LiveFeedActivity from '@/components/LiveFeedActivity'
import ActivityFilter from '@/components/utils/ActivityFilter'
import { ModalMixin } from '@/utils/mixins'

function slashEscape (contents) {
  return contents
    .replace(/\\/g, '\\\\')
    .replace(/'/g, '&apos')
    .replace(/"/g, '&quot')
    .replace(/\n/g, '<br />')
}

export default {
  name: 'UserModal',
  mixins: [Vue2Filters.mixin, ModalMixin],
  components: {
    LiveFeedActivity,
    ActivityFilter,
    Paginate
  },
  props: {
    userProp: Object,
    visible: Boolean,
    deploymentName: String,
    deploymentId: Number,
    currentIncidentId: {
      type: Number,
      default: -1
    }
  },
  data () {
    return {
      pageNum: 1,
      filterActivities: 'all',
      user: this.userProp
    }
  },
  methods: {
    changeFilter (value) {
      this.filterActivities = value
    },
    changePage (pageNum) {
      this.pageNum = pageNum
    },
    changeUser (user) {
      if (this.user.id !== user.id) {
        this.user = user
        this.filterActivities = 'all'
      }
    },
    incidentTooltip (incident) {
      return `<span><b>ID:</b> #${incident.id}<br /><b>Description:</b> ${slashEscape(incident.description)}<br /><b>Priority:</b> ${slashEscape(incident.priority)}<br /><b>Location:</b> ${slashEscape(incident.location.properties.address)}${incident.tasks.length ? `<br /><b>Tasks:<b> ${incident.tasks.filter(task => task.completedAt).length}/${incident.tasks.length}` : ''}${incident.comments.length ? `<br /><b>Updates:<b> ${incident.comments.length}` : ''}</span>`
    },
    goToIncident (incident) {
      if (this.$route.params.incidentId && parseInt(this.$route.params.incidentId) === this.currentIncidentId) {
        this.$emit('close')
      } else {
        this.$router.push({ name: 'incident', params: { deploymentName: this.deploymentName.replace(/ /g, '-'), deploymentId: this.deploymentId, incidentName: incident.name.replace(/ /g, '-'), incidentId: incident.id } })
        this.$emit('close')
      }
    },
    close () {
      this.$emit('close')
    },
    ...mapActions('users', {
      fetchUsers: 'fetchUsers'
    })
  },
  computed: {
    assignedIncidents: function () {
      return this.getIncidents.filter(incident => incident.assignedTo.some(assignedTo => assignedTo.id === this.user.id))
    },
    recentActivity: function () {
      const actvities = this.getIncidents.flatMap(incident => incident.activity.map(activity => Object.assign({}, activity, { incidentName: incident.name, incidentId: incident.id, description: incident.description, priority: incident.priority, location: incident.location.properties.address, tasks: incident.tasks.length ? `${incident.tasks.filter(task => task.completedAt).length}/${incident.tasks.length}` : null, comments: incident.comments ? incident.comments.length : null }))).filter(activity => activity.user.id === this.user.id)
      if (this.filterActivities !== 'all') {
        return actvities.filter(activity => activity.type === this.filterActivities)
      } else {
        return actvities
      }
    },
    ...mapGetters('incidents', {
      getIncidents: 'getIncidents'
    })
  }
}
</script>
