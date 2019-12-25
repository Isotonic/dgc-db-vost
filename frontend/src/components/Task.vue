<template>
  <li :class="['list-group-item', 'list-group-flush', task.completed ? 'text-muted' : '']">
      <div class="row align-items-center no-gutters">
          <div class="col mr-2">
              <h6 class="mb-0">
                  <strong>{{ task.name }} </strong><span class="text-xs">{{ taskStatusText }}</span>
              </h6>
              <span v-if="task.assignedTo.length" class="text-xs">Assigned to {{ assignedToText }}</span>
          </div>
          <div class="col-auto">
              <div>
                  <input :class="['task-checkbox', task.completed ? 'text-success' : '']" type="checkbox" :checked="task.completed">
              </div>
          </div>
      </div>
      <ol class="map-card-actions-list list-unstyled">
          <li class="map-card-actions">
            <div v-if="task.subtasks.length" v-tooltip="'Sub-Tasks'">
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
    task: Object
  },
  computed: {
    taskStatusText: function () {
      return this.task.completedAt
        ? 'Completed ' + this.$moment(this.task.completedAt).fromNow()
        : 'Created ' + this.$moment(this.task.createdAt).fromNow()
    },
    assignedToText: function () {
      if (this.task.assignedTo.length === 1) {
        return this.task.assignedTo[0]
      }
      return this.task.assignedTo.slice(0, -1).join(', ') + ' and ' + this.task.assignedTo.slice(-1)[0]
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
