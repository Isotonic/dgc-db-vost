<template>
  <vue-content-loading v-bind="$attrs" :width="300" :height="170">
    <rect x="0" y="0" rx="3" ry="3" width="300" height="170" />
  </vue-content-loading>
</template>

<script>
import VueContentLoading from 'vue-content-loading'

export default {
  name: 'VclSquare',
  components: {
    VueContentLoading
  }
}
</script>
