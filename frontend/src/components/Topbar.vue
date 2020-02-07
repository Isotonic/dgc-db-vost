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
        <input v-model="query" type="text" class="form-control bg-light small" placeholder="Search for an incident..." aria-label="Search for an incident">
        <div class="input-group-append">
          <button class="btn btn-primary" type="button">
            <i class="fas fa-search fa-sm"></i>
          </button>
        </div>
      </div>
      <div v-if="query.length" class="card-body" style="position:absolute;top:55px;left:20px;background-color:white;z-index:99;overflow-y:auto;max-height:20em">
        <ul v-for="result in queryResults" :key="result.id">
          <li :class="['list-group-item', 'list-group-flush', 'task', result.open ? '' : 'text-muted']">
            <div class="row align-items-center no-gutters">
                <div class="col mr-2">
                    <h6 class="mb-0">
                        <strong>{{ result.name }} </strong>
                    </h6>
                </div>
            </div>
          </li>
        </ul>
      </div>
      {{ queryResults.length }}
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
          <router-link :to="'logout'" class="dropdown-item"><i class="fas fa-sign-out-alt fa-sm fa-fw mr-2 text-gray-400"></i>Logout</router-link>
      </b-dropdown>
    </ul>
  </nav>
</template>

<script>
import fz from 'fuzzaldrin-plus'
import { mapGetters } from 'vuex'

export default {
  name: 'Topbar',
  props: {
    nosidebar: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      query: ''
    }
  },
  methods: {
    logout () {
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
    queryResults () {
      if (!this.query) return this.allIncidents

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
