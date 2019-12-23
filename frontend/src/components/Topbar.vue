<template>
  <nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">
    <router-link v-if="nosidebar" :to="'deployments'" class="deployments_brand_img">
      <img class="deployments_brand_img" src="@/assets/img/Logos/Default.png">
    </router-link>
    <button v-else id="sidebarToggleTop" class="btn btn-link d-md-none rounded-circle mr-3">
      <i class="fa fa-bars"></i>
    </button>
    <ul class="navbar-nav ml-auto">
      <li class="nav-item dropdown no-arrow d-sm-none">
        <div class="dropdown-menu dropdown-menu-right p-3 shadow animated--grow-in" aria-labelledby="searchDropdown">
          <form class="form-inline mr-auto w-100 navbar-search">
            <div class="input-group">
              <input type="text" class="form-control bg-light border-0 small" placeholder="Search for..." aria-label="Search" aria-describedby="basic-addon2">
              <div class="input-group-append">
                <button class="btn btn-primary" type="button">
                <i class="fas fa-search fa-sm"></i>
                </button>
              </div>
            </div>
          </form>
        </div>
      </li>
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
      <li class="nav-item dropdown no-arrow">
        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
          <span class="mr-2 d-none d-lg-inline text-gray-600 small">Test User</span>
          <img class="img-profile rounded-circle" src="#">
        </a>
        <div class="dropdown-menu dropdown-menu-right shadow animated--grow-in" aria-labelledby="userDropdown">
          <a class="dropdown-item" href="#">
            <i class="fas fa-user fa-sm fa-fw mr-2 text-gray-400"></i>
            Profile
          </a>
          <a class="dropdown-item" href="#">
            <i class="fas fa-cogs fa-sm fa-fw mr-2 text-gray-400"></i>
            Settings
          </a>
          <a class="dropdown-item" href="#">
            <i class="fas fa-list fa-sm fa-fw mr-2 text-gray-400"></i>
            Activity Log
          </a>
          <div class="dropdown-divider"></div>
          <router-link :to="'logout'" class="dropdown-item"><i class="fas fa-sign-out-alt fa-sm fa-fw mr-2 text-gray-400"></i>Logout</router-link>">
        </div>
      </li>
    </ul>
  </nav>
</template>

<script>
export default {
  name: 'Topbar',
  props: {
    nosidebar: {
      type: Boolean,
      default: false
    }
  }
}
</script>
