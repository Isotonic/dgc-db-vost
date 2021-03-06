<template>
  <li class="list-group-item list-group-flush incident-card" @click.once="goTo">
    <div class="row align-items-center no-gutters">
      <div :class="['col', 'mr-2', (!publicPage && incident.tasks.length) || incident.comments.length ?  'mb-2' : '']">
        <h6>
          <strong><text-highlight :queries="query">{{ incident.name }}</text-highlight></strong>
          <i v-if="!publicPage" :class="priorityCircle" v-tooltip="`${incident.priority} Priority`" />
        </h6>
        <p class="text-xs text-muted mb-2">Created {{ incident.createdAt | moment("from", "now") }}</p>
        <p class="text-xs mb-1"><text-highlight :queries="query">{{ incident.description }}</text-highlight></p>
        <p class="text-xs mb-0"><text-highlight :queries="query">{{ incident.location.properties.address }}</text-highlight></p>
      </div>
    </div>
    <ol v-if="incident.comments.length || (!publicPage && incident.tasks.length)" class="incident-card-actions-list list-unstyled">
      <li class="incident-card-actions">
        <div v-if="!publicPage && incident.tasks.length">
          <i class="fas fa-tasks" v-tooltip="'Tasks Complete'"></i>
          <span class="incident-card-actions-text">{{ taskText }}</span>
        </div>
        <div v-if="incident.comments.length">
          <i class="far fa-comment" v-tooltip="'Updates'"></i>
          <span class="incident-card-actions-text">{{ incident.comments.length }}</span>
        </div>
      </li>
      <ol v-if="!publicPage && incident.assignedTo.length" class="incident-card-assigned-to list-unstyled">
        <div class="avatar-group">
          <i v-for="user in incident.assignedTo" :key="user.name" class="avatar avatar-sm" v-tooltip="`${user.firstname} ${user.surname}`">
            <img alt="Avatar" :src="$developmentMode ? `http://localhost:5000${user.avatarUrl}` : user.avatarUrl" class="rounded-circle avatar-sm hover" @click="openUserModal(user)" />
          </i>
        </div>
        <user-modal v-if="isUserModalVisible" v-show="isUserModalVisible" :visible="isUserModalVisible" :deploymentName="deploymentName" :deploymentId="deploymentId" :userProp="userModal" @close="isUserModalVisible = false" />
      </ol>
    </ol>
  </li>
</template>

<script>
import TextHighlight from 'vue-text-highlight'

import UserModal from '@/components/modals/User'

export default {
  name: 'IncidentCard',
  components: {
    UserModal,
    TextHighlight
  },
  props: {
    incident: Object,
    query: String,
    deploymentName: {
      type: String,
      default: null
    },
    deploymentId: {
      type: Number,
      default: null
    },
    publicPage: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      userModal: null,
      isUserModalVisible: false
    }
  },
  methods: {
    goTo () {
      this.$emit('goTo', this.incident)
    },
    openUserModal (user) {
      this.userModal = user
      this.isUserModalVisible = true
    }
  },
  computed: {
    priorityCircle: function () {
      return `fas fa-circle ml-1 font-size-75 text-${this.incident.priority}`
    },
    taskText: function () {
      return `${this.incident.tasks.filter(task => task.completedAt).length}/${this.incident.tasks.length}`
    }
  }
}
</script>
