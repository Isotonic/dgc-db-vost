<template>
  <nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">
    <router-link v-if="nosidebar" :to="'deployments'" class="deployments_brand_img">
      <img class="deployments_brand_img" src="@/assets/img/Logos/Default.png">
    </router-link>
    <button v-else id="sidebarToggleTop" class="btn btn-link d-md-none rounded-circle mr-3">
      <i class="fa fa-bars"></i>
    </button>
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
export default {
  name: 'Topbar',
  props: {
    nosidebar: {
      type: Boolean,
      default: false
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
    }
  }
}
</script>
