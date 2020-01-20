<template>
  <li :class="['list-group-item', 'list-group-flush', task.completed ? 'text-muted' : '']" @click="open">
      <div class="row align-items-center no-gutters">
          <div class="col mr-2">
              <h6 class="mb-0">
                  <strong>{{ task.name }} </strong><span class="text-xs">{{ taskStatusText }}</span>
              </h6>
              <span v-if="task.assignedTo.length" class="text-xs">Assigned to {{ assignedToText }}</span>
          </div>
          <div class="col-auto">
            <div>
              <input :class="['task-checkbox', task.completed ? 'text-success' : '']" type="checkbox" :checked="task.completed" @click="toggle">
              <i v-if="isSubtask" class="fas fa-trash-alt btn-opacity text-danger" v-tooltip="`Delete ${task.name}`"></i>
            </div>
          </div>
      </div>
      <ol v-if="!isSubtask" class="map-card-actions-list list-unstyled">
          <li class="map-card-actions">
            <div v-if="task.subtasks.length" v-tooltip="'Subtasks'">
              <i class="fas fa-tasks"></i>
              <span class="map-card-actions-text">{{ subtaskText }}</span>
            </div>
            <div v-if="task.comments.length">
              <i class="far fa-comment" v-tooltip="'Comments'"></i>
              <span class="map-card-actions-text" v-tooltip="'Comments'">{{ task.comments.length }}</span>
            </div>
          </li>
      </ol>
  </li>
</template>

<script>
export default {
  name: 'Task',
  props: {
    task: Object,
    isSubtask: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    toggle: function () {
      event.stopPropagation()
      this.$emit('toggle', this.task.id, !this.task.completed)
    },
    open () {
      this.$emit('openModal')
    }
  },
  computed: {
    taskStatusText: function () {
      return this.task.completedAt
        ? 'Completed ' + this.$moment.unix(this.task.completedAt).fromNow()
        : 'Created ' + this.$moment.unix(this.task.createdAt).fromNow()
    },
    assignedToText: function () {
      if (this.task.assignedTo.length === 1) {
        return `${this.task.assignedTo[0].firstname} ${this.task.assignedTo[0].surname}`
      }
      return `${this.task.assignedTo.slice(0, -1).map(user => `${user.firstname} ${user.surname}`).join(', ')} and ${this.task.assignedTo.slice(-1)[0].firstname} ${this.task.assignedTo.slice(-1)[0].surname}`
    },
    subtaskText: function () {
      let completedCounter = 0
      for (let value of this.task.subtasks) {
        if (value.completedAt) {
          completedCounter += 1
        }
      }
      return completedCounter + '/' + this.task.subtasks.length
    }
  }
}
</script>
