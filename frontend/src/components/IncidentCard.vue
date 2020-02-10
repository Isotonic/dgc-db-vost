<template>
  <li class="list-group-item list-group-flush incident-card" @click="goTo">
    <div class="row align-items-center no-gutters">
      <div :class="['col', 'mr-2', incident.tasks.length || incident.comments.length ?  'mb-2' : '']">
        <h6>
          <strong><text-highlight :queries="query">{{ incident.name }}</text-highlight></strong>
          <i :class="priorityCircle" v-tooltip="`${incident.priority} Priority`" />
        </h6>
        <p class="text-xs text-muted mb-3">Created {{ incident.createdAt | moment("from", "now") }}</p>
        <p class="text-xs mb-1"><text-highlight :queries="query">{{ incident.description }}</text-highlight></p>
        <p class="text-xs mb-0"><text-highlight :queries="query">{{ incident.location.properties.address }}</text-highlight></p>
      </div>
    </div>
    <ol v-if="incident.tasks.length || incident.comments.length" class="incident-card-actions-list list-unstyled">
      <li class="incident-card-actions">
        <i v-if="incident.tasks.length" class="fas fa-tasks" v-tooltip="'Tasks'"></i>
        <span class="incident-card-actions-text">{{ taskText }}</span>
        <i v-if="incident.comments.length" class="far fa-comment" v-tooltip="'Comments'"></i>
        <span class="incident-card-actions-text">{{ incident.comments.length }}</span>
      </li>
      <ol v-if="incident.assignedTo.length" class="incident-card-assigned-to list-unstyled">
        <div class="avatar-group">
          <a v-for="user in incident.assignedTo" :key="user.name" href="#" class="avatar avatar-sm" v-tooltip="`${user.firstname} ${user.surname}`">
            <img alt="Avatar" :src="user.avatarUrl" class="rounded-circle avatar-sm">
          </a>
        </div>
      </ol>
    </ol>
  </li>
</template>

<script>
import TextHighlight from 'vue-text-highlight'

export default {
  name: 'IncidentCard',
  components: {
    TextHighlight
  },
  props: {
    incident: {
      type: Object
    },
    query: {
      type: String
    }
  },
  methods: {
    goTo: function () {
      this.$emit('goTo', this.incident)
    }
  },
  computed: {
    priorityCircle: function () {
      return `fas fa-circle ml-1 font-size-75 text-${this.incident.priority}`
    },
    taskText: function () {
      let completedCounter = 0
      for (let value of this.incident.tasks) {
        if (value.completedAt) {
          completedCounter += 1
        }
      }
      return `${completedCounter}/${this.incident.tasks.length}`
    }
  }
}
</script>
