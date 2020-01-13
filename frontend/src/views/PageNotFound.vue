<template>
  <div>
    <topbar v-if="loggedIn" :nosidebar="true" />
    <div class="text-center">
      <div class="error mx-auto" data-text="404">404</div>
      <p class="lead text-gray-800 mb-5">Page Not Found</p>
      <p class="text-gray-500 mb-0">It looks like you found a page that doesn't exist.</p>
      <router-link :to="'/deployments'">&larr; Back to Deployments</router-link>
    </div>
  </div>
</template>

<script>
import Topbar from '@/components/Topbar.vue'

export default {
  name: 'PageNotFound',
  data () {
    return {
      loggedIn: true
    }
  },
  components: {
    Topbar
  }
}
</script>
