<template>
  <li :class="['list-group-item', 'list-group-flush', 'task', task.completed ? 'text-muted' : '']" @click="open">
    <div class="row align-items-center no-gutters">
        <div class="col mr-2">
            <h6 class="mb-0">
                <strong>{{ task.name }} </strong>
                <span class="text-xs">{{ taskStatusText }}</span>
            </h6>
            <span v-if="task.assignedTo.length" class="text-xs">Assigned to {{ assignedToText }}</span>
        </div>
        <div>
          <input :class="['mr-2', task.completed ? 'text-success' : '']" type="checkbox" :checked="task.completed" @click="toggle">
        </div>
    </div>
    <div v-if="task.tags.length" class="mt-2 mb-1">
      <span v-for="tag in task.tags" :key="tag" :class="['badge', 'badge-pill', 'mr-2', tagClass(tag)]">
        {{ tag }}
      </span>
    </div>
    <ol v-if="task.subtasks.length || task.comments.length" class="incident-card-actions-list list-unstyled">
      <li class="incident-card-actions">
        <div v-if="task.subtasks.length" v-tooltip="'Subtasks'">
          <i class="fas fa-tasks"></i>
          <span class="incident-card-actions-text">{{ subtaskText }}</span>
        </div>
        <div v-if="task.comments.length">
          <i class="far fa-comment" v-tooltip="'Comments'"></i>
          <span class="incident-card-actions-text" v-tooltip="'Comments'">{{ task.comments.length }}</span>
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
  data () {
    return {
      isQuestionModalVisible: false,
      edit: false
    }
  },
  methods: {
    toggle: function () {
      event.stopPropagation()
      this.edit = false
      this.$emit('toggle', this.task.id, !this.task.completed)
    },
    open () {
      this.$emit('openModal')
    },
    tagClass (tag) {
      if (tag === 'High Priority') {
        return 'badge-danger'
      } else if (tag === 'Medium Priority') {
        return 'badge-orange'
      } else if (tag === 'Low Priority') {
        return 'badge-warning'
      } else {
        return 'badge-primary'
      }
    }
  },
  computed: {
    taskStatusText: function () {
      return this.task.completed
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
      return `${this.task.subtasks.filter(subtask => subtask.completedAt).length}/${this.task.subtasks.length}`
    }
  }
}
</script>
