<template>
  <div v-if="data.assignedTo.length" class="avatar-group">
    <a v-for="user in data.assignedTo" :key="user.id" href="#" class="avatar avatar-sm" v-tooltip="`${user.firstname} ${user.surname}`">
      <img alt="Avatar" :src="user.avatarUrl" class="rounded-circle avatar-sm">
    </a>
  </div>
  <div v-else>
    Unassigned
  </div>
</template>

<script>
export default {
  props: ['data', 'index']
}
</script>
