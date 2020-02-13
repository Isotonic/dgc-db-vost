<template>
  <div id="wrapper">
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar v-if="isLoggedIn" :nosidebar="true" />
      <div class="text-center">
        <div class="error mx-auto" data-text="404">404</div>
        <p class="lead text-gray-800 mb-5">Page Not Found</p>
        <p class="text-gray-500 mb-0">It looks like you found a page that doesn't exist.</p>
        <router-link :to="{ name: 'deployments' }">&larr; Back to Deployments</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

import Topbar from '@/components/Topbar'

export default {
  name: 'PageNotFound',
  components: {
    Topbar
  },
  methods: {
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    })
  },
  computed: {
    ...mapGetters('user', {
      isLoggedIn: 'loggedIn'
    })
  },
  async created () {
    this.checkUserLoaded()
  }
}
</script>
