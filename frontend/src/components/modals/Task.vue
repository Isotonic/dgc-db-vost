<template>
  <Modal :title="task.name" :bigger="true" @close="close">
    <div class="row">
      <div class="col-xl-12 col-sm-8 mb-4">
        <h5>
          <i class="fas fa-align-left mb-3 mr-2"></i> Description
        </h5>
        <textarea class="form-control-plaintext text-dark mb-3" name="description" :placeholder="task.description"></textarea>
        <h6>Change Assigned Members</h6>
        <button type="submit" class="btn btn-primary mt-3 float-right d-none">Save</button>
      </div>
    </div>
    <div class="row">
      <div class="col-xl-12 col-sm-8 mb-2">
        <h5>
          <i class="fas fa-tasks mb-3 mr-2"></i> Tasks
        </h5>
        <div class="row">
          <div class="col-auto">
            <div class="h5 ml-1 mb-2 font-weight-bold text-gray-800">{{ calculateProgressPercentage }}%</div>
          </div>
          <div class="col">
            <div class="progress progress-sm mt-2">
              <div :class="['progress-bar', calculateProgressColour]" :style="{ width: calculateProgressPercentage + '%' }" aria-valuenow="9" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
          </div>
        </div>
        <ul class="list-group">
          <task v-for="subtask in task.subtasks" :key="subtask.id" :task="subtask" :isSubtask="true"></task>
        </ul>
      </div>
      <div class="col-xl-12 col-sm-8 mb-4">
        <h5><i class="fas fa-comments mb-3 mr-2"></i> Comments</h5>
        <ul class="list-unstyled">
          <comment v-for="comment in task.comments" :key="comment.id" :comment="comment"></comment>
        </ul>
        <form role="form">
          <div class="form-group input-group mb-5">
            <input class="form-control was-validated" name="comment" placeholder="Add a comment..." type="text" required>
            <button type="button" class="btn btn-primary ml-3">Submit</button>
          </div>
        </form>
        <h5>
          <i class="fas fa-clipboard-list mb-3 mr-2"></i> Actions
        </h5>
        <ul class="activity">
          <activity v-for="action in orderBy(task.logs, 'occurredAt')" :key="action.id" :action="action"></activity>
        </ul>
      </div>
    </div>
  </Modal>
</template>

<script>
import Vue2Filters from 'vue2-filters'

import Task from '@/components/Task'
import Comment from '@/components/Comment'
import Activity from '@/components/Activity'
import Modal from '@/components/utils/Modal'

export default {
  name: 'TaskModal',
  mixins: [Vue2Filters.mixin],
  components: {
    Task,
    Comment,
    Activity,
    Modal
  },
  props: {
    visible: Boolean,
    task: Object
  },
  methods: {
    close () {
      this.$emit('close')
    }
  },
  computed: {
    calculateProgressPercentage: function () {
      let completedCounter = 0
      for (let value of this.task.subtasks) {
        if (value.completed) {
          completedCounter += 1
        }
      }
      return Math.round((completedCounter / this.task.subtasks.length) * 100)
    },
    calculateProgressColour: function () {
      let percentage = this.calculateProgressPercentage
      return {
        'bg-success': percentage >= 80,
        'bg-orange': percentage >= 50 && percentage < 80,
        'bg-warning': percentage >= 25 && percentage < 50,
        'bg-danger': percentage >= 0 && percentage < 25
      }
    }
  },
  watch: {
    visible: function () {
      if (this.visible) {
        return document.body.classList.add('modal-open')
      }
      document.body.classList.remove('modal-open')
    }
  },
  created: function () {
    if (this.visible) {
      document.body.classList.add('modal-open')
    }
  }
}
</script>
