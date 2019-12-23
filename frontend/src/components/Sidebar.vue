<template>
  <div>
    <ul class="navbar-nav bg-gradient-primary sidebar sidebar-dark accordion" id="accordionSidebar">
      <a class="sidebar-brand d-flex align-items-center justify-content-center" href="routerline">
        <img class="mx-4" src="@/assets/img/Logos/White.png">
      </a>
      <hr class="sidebar-divider my-0">
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-list"></i>
        <span>Deployments</span></a>
      </li>
      <hr class="sidebar-divider">
      <div class="sidebar-heading">
        { title }
      </div>
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-clone"></i>
        <span>Incidents</span></a>
      </li>
        <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-clone"></i>
        <span>Assigned Incidents</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-clone"></i>
        <span>Closed Incidents</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-bell"></i>
        <span>Notifications</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-map-marker-alt"></i>
        <span>Map</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-rss"></i>
        <span>Live Feed</span></a>
      </li>
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-pen"></i>
        <span>Decision-Making Log</span></a>
      </li>
      <hr class="sidebar-divider">
      <div class="sidebar-heading">
        Supervisor
      </div>
      <li class="nav-item">
        <a class="nav-link" href="routerline">
        <i class="fas fa-fw fa-flag"></i>
        <span>Actions Required </span></a>
      </li>
      <hr class="sidebar-divider d-none d-md-block">
      <div class="text-center d-none d-md-inline">
        <button class="rounded-circle border-0" id="sidebarToggle"></button>
      </div>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'Sidebar',
  props: {
    title: String
  }
}
</script>
