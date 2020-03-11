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
      <li v-if="!publicPage" class="nav-item dropdown no-arrow mx-1">
        <a class="nav-link dropdown-toggle" id="notificationDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          <i class="fas fa-bell fa-fw"></i>
            <span class="badge badge-danger badge-counter"></span>
        </a>
        <div class="dropdown-list dropdown-menu dropdown-menu-right shadow animated--grow-in" aria-labelledby="notificationDropdown">
          <h6 class="dropdown-header">
            Notification Center
          </h6>
          <a class="dropdown-item text-center small text-gray-500">No Notifications</a>
        </div>
      </li>
      <div v-if="!publicPage" class="topbar-divider d-none d-sm-block"></div>
      <b-dropdown v-if="!publicPage" variant="link" size="xs" toggle-tag="li" toggle-class="nav-item">
        <template slot="button-content">
            <a class="nav-link">
              <span class="mr-2 d-none d-lg-inline text-gray-600 small">{{ name }}</span>
              <img class="img-profile rounded-circle" :src="avatarUrl">
            </a>
        </template>
        <b-dropdown-item><i class="fas fa-cogs fa-sm fa-fw mr-2 text-gray-400"></i>Settings</b-dropdown-item>
        <b-dropdown-item v-if="hasPermission('Supervisor')" @click="adminSettings"><i class="fas fa-users-cog fa-sm fa-fw mr-2 text-gray-400"></i>Admin</b-dropdown-item>
        <div class="dropdown-divider"></div>
        <b-dropdown-item @click="logout"><i class="fas fa-sign-out-alt fa-sm fa-fw mr-2 text-gray-400"></i>Logout</b-dropdown-item>
      </b-dropdown>
    </ul>
  </nav>
</template>

<script>
import _ from 'lodash'
import fz from 'fuzzaldrin-plus'
import router from '@/router/index'
import { mapGetters } from 'vuex'

import IncidentCard from '@/components/IncidentCard'

export default {
  name: 'Topbar',
  components: {
    IncidentCard
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
      hideResults: false
    }
  },
  methods: {
    goTo: function (incident) {
      if (!this.$route.params.incidentId || parseInt(this.$route.params.incidentId) !== incident.id) {
        router.push({ name: 'incident', params: { deploymentName: this.deploymentName.replace(/ /g, '-'), deploymentId: this.deploymentId, incidentName: incident.name.replace(' ', '-'), incidentId: incident.id } })
      }
      this.query = ''
    },
    delayBlur: function () {
      const that = this
      setTimeout(function () { that.hideResults = true }, 400)
    },
    adminSettings: function () {
      router.push({ name: 'admin' })
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
