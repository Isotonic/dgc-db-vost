<template>
  <nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">
    <router-link v-if="nosidebar" :to="'deployments'" class="deployments_brand_img">
      <img class="deployments_brand_img" src="@/assets/img/Logos/Default.png">
    </router-link>
    <button v-else id="sidebarToggleTop" class="btn btn-link d-md-none rounded-circle mr-3">
      <i class="fa fa-bars"></i>
    </button>
    <div v-if="!nosidebar">
      <div class="ml-md-2 my-2 my-md-0 navbar-search input-group">
        <input v-model="queryDebounced" type="text" :class="['form-control', 'bg-light', 'small', queryDebounced.length ? 'navbar-search-results' : '']" placeholder="Search for an incident..." aria-label="Search for an incident" @focus="hideResults = false" @blur="hideResults = true">
        <div class="input-group-append">
          <div class="btn bg-primary">
            <i class="fas fa-search fa-sm text-white" />
          </div>
        </div>
      </div>
      <div v-if="queryDebounced.length && !hideResults" class="card-body search-results px-0 py-0">
        <ul class="mb-4 pl-0">
          <incident-card v-for="incident in queryResults" :key="incident.id" :incident="incident" :query="queryDebounced" @goTo="goTo" />
          <li v-if="!queryResults.length" class="text-center list-unstyled mt-3"><span class="font-weight-bold">No results found</span></li>
        </ul>
      </div>
    </div>
    <ul class="navbar-nav ml-auto">
      <li class="nav-item dropdown no-arrow mx-1">
        <a class="nav-link dropdown-toggle" href="#" id="notificationDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          <i class="fas fa-bell fa-fw"></i>
            <span class="badge badge-danger badge-counter"></span>
        </a>
        <div class="dropdown-list dropdown-menu dropdown-menu-right shadow animated--grow-in" aria-labelledby="notificationDropdown">
          <h6 class="dropdown-header">
            Notification Center
          </h6>
          <a class="dropdown-item text-center small text-gray-500" href="#">No Notifications</a>
        </div>
      </li>
      <div class="topbar-divider d-none d-sm-block"></div>
      <b-dropdown variant="link" size="xs" toggle-tag="li" toggle-class="nav-item">
          <template slot="button-content">
              <a class="nav-link">
                <span class="mr-2 d-none d-lg-inline text-gray-600 small">{{ name }}</span>
                <img class="img-profile rounded-circle" :src="avatarUrl">
              </a>
          </template>
          <b-dropdown-item><i class="fas fa-user fa-sm fa-fw mr-2 text-gray-400"></i>Profile</b-dropdown-item>
          <b-dropdown-item><i class="fas fa-cogs fa-sm fa-fw mr-2 text-gray-400"></i>Settings</b-dropdown-item>
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
      router.push({ name: 'incident', params: { deploymentName: this.deploymentName.replace(' ', '-'), deploymentId: this.deploymentId, incidentName: incident.name.replace(' ', '-'), incidentId: incident.id } })
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
    ...mapGetters({
      allIncidents: 'incidents/getIncidents'
    })
  }
}
</script>
