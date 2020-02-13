<template>
  <ul class="navbar-nav bg-gradient-primary sidebar sidebar-dark accordion" id="accordionSidebar">
    <router-link :to="{ name: 'deployments' }" class="sidebar-brand d-flex align-items-center justify-content-center">
      <img class="mx-4" src="@/assets/img/Logos/White.png">
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
      <router-link :to="{ name: 'notifications' }" class="nav-link">
        <i class="fas fa-fw fa-bell"></i>
        <span>Notifications</span>
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
    <li class="nav-item">
      <router-link :to="{ name: 'decisionMakingLog', params: {deploymentName: deploymentName.replace(/ /g, '-'), deploymentId: deploymentId} }" class="nav-link">
        <i class="fas fa-fw fa-pen"></i>
        <span>Decision-Making Log</span>
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
          <span>Actions Required </span>
        </router-link>
      </li>
    </div>
    <hr class="sidebar-divider d-none d-md-block">
    <div class="text-center d-none d-md-inline">
      <button class="rounded-circle border-0" id="sidebarToggle"></button>
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
  computed: {
    isSupervisor: function () {
      return this.$store.getters['user/hasPermission']('supervisor')
    }
  }
}
</script>
