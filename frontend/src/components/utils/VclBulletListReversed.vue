<template>
  <vue-content-loading v-bind="$attrs" :width="300" :height="120">
    <rect x="10" y="13" rx="4" ry="4" width="200" height="13" />
    <rect x="10" y="41" rx="4" ry="4" width="180" height="8" />
    <rect x="10" y="64" rx="4" ry="4" width="150" height="8" />
    <rect x="10" y="87" rx="4" ry="4" width="250" height="8" />
    <circle cx="255" cy="30" r="30" />
  </vue-content-loading>
</template>

<script>
import VueContentLoading from 'vue-content-loading'

export default {
  components: {
    VueContentLoading
  }
}
</script>
