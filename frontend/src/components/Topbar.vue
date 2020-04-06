<template>
  <nav :class="['navbar', 'navbar-expand', 'navbar-light', 'bg-white', 'topbar', 'static-top shadow', noMargin ? '' : 'mb-4']">
    <router-link v-if="nosidebar || noSearchBar" :to="{ name: goToDeployments ? 'deployments' : 'publicMap' }" class="deployments_brand_img">
      <img class="deployments_brand_img" src="@/assets/img/Logos/Default.png">
    </router-link>
    <button v-else class="btn btn-link d-md-none rounded-circle mr-3" @click="$emit('toggleSidebar')">
      <i class="fa fa-bars"></i>
    </button>
    <div v-if="!nosidebar">
      <div v-if="!noSearchBar" class="ml-md-2 my-2 my-md-0 navbar-search input-group">
        <input v-model="queryDebounced" type="text" :class="['form-control', 'bg-light', 'small', queryDebounced.length ? 'navbar-search-results' : '']" placeholder="Search for an incident..." aria-label="Search for an incident" tabindex="-1" @focus="hideResults = false" @blur="delayBlur">
        <div class="input-group-append">
          <div class="btn bg-primary">
            <i class="fas fa-search fa-sm text-white" />
          </div>
        </div>
      </div>
      <div v-if="queryDebounced.length && !hideResults" class="card-body search-results px-0 py-0">
        <ul class="mb-4 pl-0">
          <incident-card v-for="incident in queryResults" :key="incident.id" :deploymentName="deploymentName" :deploymentId="deploymentId" :incident="incident" :query="queryDebounced" @goTo="goTo" />
          <li v-if="!queryResults.length" class="text-center list-unstyled mt-3"><span class="font-weight-bold">No results found</span></li>
        </ul>
      </div>
    </div>
    <ul class="navbar-nav ml-auto">
      <router-link v-if="publicPage" :to="{ name: !user ? 'login' : 'deployments' }">
        <button class="btn btn-icon-split btn-primary">
          <span class="btn-icon">
              <i :class="['fas', !user ? 'fa-sign-in-alt' : 'fa-list']"></i>
          </span>
          <span class="text">{{ !user ? 'Login' : 'View Deployments' }}</span>
        </button>
      </router-link>
      <b-dropdown v-if="!publicPage && user" variant="link" size="xs" toggle-tag="li" toggle-class="nav-item" menu-class="dropdown-list dropdown-menu dropdown-menu-right shadow">
        <template slot="button-content">
          <a class="nav-link dropdown-toggle" id="notificationDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i class="fas fa-bell fa-fw"></i>
            <span v-if="user.notifications.length" class="badge badge-danger badge-counter">{{ user.notifications.length }}</span>
          </a>
        </template>
        <b-dropdown-header>
          <h6 class="font-weight-bold text-center mb-0">Notification Center</h6>
        </b-dropdown-header>
        <div v-if="user.notifications.length" class="notifications">
          <span class="dropdown-item text-center text-primary font-weight-bold" @click="markAllAsRead">
            Mark All As Read
          </span>
          <a v-for="notification in orderBy(user.notifications, 'occurredAt', -1)" :key="notification.id" class="dropdown-item d-flex align-items-center" @click="goToNotification(notification)">
            <div class="mr-3">
              <img alt="Avatar" :src="$developmentMode ? `http://localhost:5000${notification.triggeredBy.avatarUrl}` : notification.triggeredBy.avatarUrl" class="rounded-circle avatar-md hover" />
            </div>
            <div>
              <div class="small text-gray-500">{{ notification.occurredAt | moment("from", "now") }}</div>
              <div v-if="notification.type === 'flagged_incident'">
                <span class="font-weight-bold">{{ notification.triggeredBy.firstname }} {{ notification.triggeredBy.surname }}</span> has flagged <span class="font-weight-bold">{{ notification.incidentName }} with reason:</span><span> {{ notification.reason }}</span>
              </div>
              <div v-else>
                <span class="font-weight-bold">{{ notification.triggeredBy.firstname }} {{ notification.triggeredBy.surname }}</span> {{ notificationType(notification.type) }} <span class="font-weight-bold">{{ nameType(notification) }}.</span>
              </div>
            </div>
          </a>
        </div>
        <span v-if="user && !user.notifications.length" class="dropdown-item disabled text-center small text-gray-500">No Notifications</span>
      </b-dropdown>
      <div v-if="!publicPage" class="topbar-divider d-none d-sm-block"></div>
      <b-dropdown v-if="!publicPage" variant="link" size="xs" toggle-tag="li" toggle-class="nav-item">
        <template slot="button-content">
            <a class="nav-link">
              <span class="mr-2 d-none d-lg-inline text-gray-600 small">{{ name }}</span>
              <img class="img-profile rounded-circle" :src="$developmentMode ? `http://localhost:5000${avatarUrl}` : avatarUrl">
            </a>
        </template>
        <b-dropdown-item @click="isAccountSettingsModalVisible = true"><i class="fas fa-cogs fa-sm fa-fw mr-2 text-gray-400"></i>Account</b-dropdown-item>
        <b-dropdown-item v-if="hasPermission('Supervisor')" @click="adminSettings"><i class="fas fa-users-cog fa-sm fa-fw mr-2 text-gray-400"></i>Admin</b-dropdown-item>
        <div class="dropdown-divider"></div>
        <b-dropdown-item @click="logout"><i class="fas fa-sign-out-alt fa-sm fa-fw mr-2 text-gray-400"></i>Logout</b-dropdown-item>
      </b-dropdown>
      <account-settings-modal v-if="isAccountSettingsModalVisible" v-show="isAccountSettingsModalVisible" :visible="isAccountSettingsModalVisible" @close="isAccountSettingsModalVisible = false" />
    </ul>
  </nav>
</template>

<script>
import _ from 'lodash'
import Vue from 'vue'
import fz from 'fuzzaldrin-plus'
import router from '@/router/index'
import Vue2Filters from 'vue2-filters'
import { mapGetters } from 'vuex'

import IncidentCard from '@/components/IncidentCard'
import AccountSettingsModal from '@/components/modals/AccountSettings'

const typeStrings = {
  'assigned_incident': 'has assigned you to',
  'unassigned_incident': 'has unassigned you from',
  'assigned_task': 'has assigned you to task',
  'unassigned_task': 'has unassigned you from task',
  'assigned_subtask': 'has assigned you to subtask',
  'unassigned_subtask': 'has unassigned you from subtask'
}

export default {
  name: 'Topbar',
  mixins: [Vue2Filters.mixin],
  components: {
    IncidentCard,
    AccountSettingsModal
  },
  props: {
    deploymentId: Number,
    deploymentName: String,
    nosidebar: {
      type: Boolean,
      default: false
    },
    noSearchBar: {
      type: Boolean,
      default: false
    },
    publicPage: {
      type: Boolean,
      default: false
    },
    noMargin: {
      type: Boolean,
      default: false
    },
    goToDeployments: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      query: '',
      hideResults: false,
      isAccountSettingsModalVisible: false
    }
  },
  methods: {
    goTo: function (incident) {
      if (!this.$route.params.incidentId || parseInt(this.$route.params.incidentId) !== incident.id) {
        router.push({ name: 'incident', params: { deploymentName: this.deploymentName.replace(/ /g, '-'), deploymentId: this.deploymentId, incidentName: incident.name.replace(' ', '-'), incidentId: incident.id } })
      }
      this.query = ''
    },
    goToNotification: function (notification) {
      if (notification.type !== 'unassigned_incident' && (!this.$route.params.incidentId || parseInt(this.$route.params.incidentId) !== notification.incidentId)) {
        router.push({ name: 'incident', params: { deploymentName: notification.deploymentName.replace(/ /g, '-'), deploymentId: notification.deploymentId, incidentName: notification.incidentName.replace(' ', '-'), incidentId: notification.incidentId } })
      }
      this.ApiDelete(`/notifications/${notification.id}`)
        .then(() => Vue.noty.success('Marked notification as read.'))
    },
    markAllAsRead: function () {
      this.ApiDelete(`/notifications`)
        .then(() => Vue.noty.success('Marked all notification as read.'))
    },
    delayBlur: function () {
      const that = this
      setTimeout(function () { that.hideResults = true }, 400)
    },
    adminSettings: function () {
      router.push({ name: 'admin' })
    },
    notificationType: function (type) {
      return typeStrings[type]
    },
    nameType: function (notification) {
      if (notification.subtaskName !== null) {
        return notification.subtaskName
      } else if (notification.taskName !== null) {
        return notification.taskName
      } else {
        return notification.incidentName
      }
    },
    logout: function () {
      this.$store.dispatch('user/logout')
    }
  },
  computed: {
    name: function () {
      return this.$store.getters['user/getName']
    },
    avatarUrl: function () {
      return this.$store.getters['user/getAvatarUrl']
    },
    queryDebounced: {
      get () {
        return this.query
      },
      set: _.debounce(function (newValue) {
        this.query = newValue
        this.hideResults = false
      }, 100)
    },
    queryResults () {
      if (!this.query) {
        return this.allIncidents
      }

      const preparedQuery = fz.prepareQuery(this.query)
      const scores = {}

      return this.allIncidents
        .map((incident, index) => {
          const scorableFields = [
            incident.name,
            incident.description,
            incident.location.properties.address
          ].map(toScore => fz.score(toScore, this.query, { preparedQuery }))

          scores[incident.id] = Math.max(...scorableFields)

          return incident
        })
        .filter(option => scores[option.id] > 1)
        .sort((a, b) => scores[b.id] - scores[a.id])
    },
    ...mapGetters('user', {
      hasPermission: 'hasPermission',
      user: 'getUser'
    }),
    ...mapGetters('incidents', {
      allIncidents: 'getIncidents'
    })
  }
}
</script>
