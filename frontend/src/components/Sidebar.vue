<template>
  <ul :class="['navbar-nav', 'bg-gradient-primary', 'sidebar', 'sidebar-dark', 'accordion', hasClass ? 'toggle-sidebar' : '', minimised ? 'toggled' : '']" ref="sidebar">
    <router-link :to="{ name: 'deployments' }" class="sidebar-brand d-flex align-items-center justify-content-center">
      <img src="@/assets/img/Logos/White.png">
    </router-link>
    <hr class="sidebar-divider my-0">
    <li class="nav-item">
      <router-link :to="{ name: 'deployments' }" class="nav-link">
        <i class="fas fa-fw fa-list"></i>
        <span>Deployments</span>
      </router-link>
    </li>
    <hr class="sidebar-divider">
    <div class="sidebar-heading">
      {{ deploymentName }}
    </div>
    <li class="nav-item">
      <router-link :to="{ name: 'incidents', params: {deploymentName: deploymentName.replace(/ /g, '-'), deploymentId: deploymentId} }" class="nav-link">
        <i class="fas fa-fw fa-clone"></i>
        <span>Incidents</span>
      </router-link>
    </li>
    <li class="nav-item">
      <router-link :to="{ name: 'map', params: {deploymentName: deploymentName.replace(/ /g, '-'), deploymentId: deploymentId} }" class="nav-link">
        <i class="fas fa-fw fa-map-marker-alt"></i>
        <span>Map</span>
      </router-link>
    </li>
    <li class="nav-item">
      <router-link :to="{ name: 'liveFeed', params: {deploymentName: deploymentName.replace(/ /g, '-'), deploymentId: deploymentId} }" class="nav-link">
        <i class="fas fa-fw fa-rss"></i>
        <span>Live Feed</span>
      </router-link>
    </li>
    <div v-if="isSupervisor">
      <hr class="sidebar-divider">
      <div class="sidebar-heading">
        Supervisor
      </div>
      <li class="nav-item">
        <router-link :to="{ name: 'actionsRequired', params: {deploymentName: deploymentName.replace(/ /g, '-'), deploymentId: deploymentId} }" class="nav-link">
          <i class="fas fa-fw fa-flag"></i>
          <span>Actions Required
            <span v-if="actionsRequired > 0"  class="badge badge-light ml-1">{{ actionsRequired }}</span>
            </span>
        </router-link>
      </li>
    </div>
    <hr class="sidebar-divider d-none d-md-block">
    <div class="text-center d-none d-md-inline">
      <button class="rounded-circle border-0" id="sidebarToggle" @click="minimised = !minimised"></button>
    </div>
  </ul>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    deploymentId: Number,
    deploymentName: String
  },
  data () {
    return {
      hasClass: true,
      minimised: false
    }
  },
  methods: {
    toggleSidebar: function () {
      this.hasClass = !this.hasClass
      this.minimised = false
    }
  },
  computed: {
    isSupervisor: function () {
      return this.$store.getters['user/hasPermission']('supervisor')
    },
    actionsRequired: function () {
      return this.$store.getters['incidents/getActionsRequiredAmount']
    }
  },
  watch: {
    minimised (value) {
      localStorage.minimiseSidebar = value
    }
  },
  async created () {
    if (localStorage.minimiseSidebar) {
      this.minimised = JSON.parse(localStorage.minimiseSidebar)
    }
  }
}
</script>
