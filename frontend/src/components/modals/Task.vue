<template>
  <modal :title="task.name" :bigger="true" :bgLight="true" @close="close">
    <div class="row">
      <div class="col-xl-12 col-sm-8 mb-1">
        <div class="mb-3">
          <h5>
            <i class="fas fa-align-left mr-2"></i>
            <span class="font-weight-bold"> Description</span>
            <div class="float-right">
              <b-dropdown id="ChangeTaskNameDropdown" size="xs" right menu-class="mt-3 width-15" variant="link" toggle-tag="div" offset="100" @shown="openedTaskNameDropdown" @hidden="closedTaskNameDropdown">
                <template slot="button-content">
                  <a class="fas fa-edit mr-3 text-black hover-primary" aria-haspopup="true" v-tooltip="'Change Task Name'"></a>
                </template>
                <h6 class="text-primary text-center font-weight-bold">Change Task Name</h6>
                <b-dropdown-divider />
                <div class="pl-1 pr-1">
                  <input v-model="changeTaskName" class="form-control mb-2 mt-3" placeholder="Task name" type="text" required>
                  <i v-if="changeTaskName !== task.name" id="reset-task-name" class="fa fa-times" @click="changeTaskName = task.name"/>
                </div>
              </b-dropdown>
              <b-dropdown id="ChangeAssignedDropdown" size="xs" right menu-class="mt-3 width-15" variant="link" toggle-tag="div" offset="100" @shown="openedAssignedDropdown" @hidden="closedAssignedDropdown">
                <template slot="button-content">
                  <a class="fas fa-users-cog mr-3 text-black hover-primary" aria-haspopup="true" v-tooltip="'Change Assigned'"></a>
                </template>
                <h6 class="text-primary text-center font-weight-bold">Change Assigned</h6>
                <b-dropdown-divider />
                <div class="pl-1 pr-1">
                  <multiselect v-model="assignedSelected" :options="selectOptions" :multiple="true" group-values="users" group-label="name" :group-select="true" placeholder="Type to search" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} user${count > 1 ? 's' : ''} assigned.`" :blockKeys="['Delete']" selectLabel="" selectGroupLabel="" deselectLabel="" deselectGroupLabel="" selectedLabel="" :loading="isSelectLoading">
                    <template v-if="didAssignedChange" slot="clear">
                      <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setAssignedSelecter"></div>
                    </template>
                    <span slot="noResult">Oops! No user found.</span>
                  </multiselect>
                </div>
              </b-dropdown>
              <b-dropdown id="ChangeTagsDropdown" size="xs" right menu-class="mt-3 width-15" variant="link" toggle-tag="div" offset="100" @hidden="closedTagsDropdown">
                <template slot="button-content">
                  <a class="fas fa-tags mr-3 text-black hover-primary" aria-haspopup="true" v-tooltip="'Change Tags'"></a>
                </template>
                <h6 class="text-primary text-center font-weight-bold">Change Tags</h6>
                <b-dropdown-divider />
                <div class="pl-1 pr-1">
                  <multiselect v-model="tagsSelected" tag-placeholder="Add this as new tag" placeholder="Search or create a tag" :options="tagOptions" :multiple="true" :taggable="true" @tag="addTag" :closeOnSelect="false" :limit="0" :limitText="count => `${count} tag${count > 1 ? 's' : ''} assigned.`" selectLabel="" deselectLabel="" selectedLabel="" />
                </div>
              </b-dropdown>
              <b-dropdown id="DeleteTaskDropdown" ref="DeleteTaskDropdown" size="xs" right menu-class="mt-3" variant="link" toggle-tag="div" offset="60">
                <template slot="button-content">
                  <a class="fas fa-trash-alt text-black hover-danger" aria-haspopup="true" v-tooltip="'Delete Task'"></a>
                </template>
                <h6 class="text-primary text-center font-weight-bold">Are you sure?</h6>
                <b-dropdown-divider />
                <div class="text-center">
                  <button class="btn btn-m btn-success mr-1" @click="deleteTask">Yes</button>
                  <button class="btn btn-m btn-danger ml-1" @click="hideDeleteDropdown">No</button>
                </div>
              </b-dropdown>
            </div>
          </h5>
        </div>
        <textarea-autosize class="form-control-plaintext text-dark" placeholder="Add a description" v-model="newDescription" :min-height="10" :max-height="350"/>
        <i v-if="hasTypedDescription" class="fas fa-times ml-3 text-black float-right" @click="newDescription = task.description" v-tooltip="'Cancel'"></i>
        <i v-if="hasTypedDescription" class="fas fa-check hover ml-3 text-black float-right" @click="updateDescription" v-tooltip="'Save'"></i>
        <div v-if="task.tags.length" class="mb-3">
          <span v-for="tag in task.tags" :key="tag" :class="['badge', 'badge-pill', 'mr-2', tagClass(tag)]">
            {{ tag }}
          </span>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-xl-12 col-sm-8 mb-4">
        <h5>
          <i class="fas fa-tasks mb-3 mr-2"></i>
          <span class="font-weight-bold"> Subtasks</span>
        </h5>
        <div v-if="task.subtasks.length" class="row">
          <div class="col-auto">
            <div class="h5 ml-1 mb-2 font-weight-bold text-gray-800">{{ calculateProgressPercentage }}%</div>
          </div>
          <div class="col">
            <div class="progress progress-sm mt-2 mb-4">
              <div :class="['progress-bar', calculateProgressColour]" :style="{ width: calculateProgressPercentage + '%' }" :aria-valuenow="calculateProgressPercentage" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
          </div>
        </div>
        <ul class="list-group">
          <subtask v-for="subtask in orderBy(task.subtasks, 'createdAt')" :key="subtask.id" :subtask="subtask" :deploymentId="deploymentId" @toggle="toggle" />
        </ul>
        <form @submit.prevent="handleSubmit" aria-label="Add a new subtask">
          <input v-model="subtaskName" class="form-control mb-2 mt-3" placeholder="Subtask name" type="text" required>
          <multiselect v-model="subtaskAssignedSelected" :options="selectOptions" :multiple="true" group-values="users" group-label="name" :group-select="true" placeholder="Assign users to the subtask" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} user${count > 1 ? 's' : ''} assigned.`" :blockKeys="['Delete']" selectLabel="" selectGroupLabel="" deselectLabel="" deselectGroupLabel="" selectedLabel="" :loading="isSelectLoading">
            <template v-if="didSubtaskAssignedChange" slot="clear">
              <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="subtaskAssignedSelected = []"></div>
            </template>
            <span slot="noResult">Oops! No user found.</span>
          </multiselect>
          <div class="text-right">
            <button type="submit" class="btn btn-primary mt-2">Create</button>
          </div>
        </form>
      </div>
      <div class="col-xl-12 col-sm-8 mt-4 mb-4">
        <h5>
          <i class="fas fa-comments mb-3 mr-2"></i>
          <span class="font-weight-bold"> Comments</span>
        </h5>
        <ul class="list-unstyled">
          <task-comment v-for="comment in task.comments" :key="comment.id" :comment="comment" :deploymentName="deploymentName" :deploymentId="deploymentId" :incidentId="incidentId" />
        </ul>
        <comment-box :placeholder="'Add a comment...'" @submitComment="submitComment" ref="commentBox" />
      </div>
      <div class="col-xl-12 col-sm-8 mt-4">
        <h5>
          <i class="fas fa-clipboard-list mb-2 mr-2"></i>
          <span class="font-weight-bold"> Activity</span>
        </h5>
        <ul class="activity">
          <task-activity v-for="action in orderBy(task.activity, 'occurredAt', -1)" :key="action.id" :action="action" :deploymentName="deploymentName" :deploymentId="deploymentId" :incidentId="incidentId" />
        </ul>
      </div>
    </div>
  </modal>
</template>

<script>
import Vue2Filters from 'vue2-filters'
import Multiselect from 'vue-multiselect'
import { mapGetters, mapActions } from 'vuex'

import CommentBox from '../CommentBox'
import Subtask from '@/components/Subtask'
import TaskComment from '@/components/TaskComment'
import TaskActivity from '@/components/TaskActivity'
import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'TaskModal',
  mixins: [Vue2Filters.mixin, ModalMixin],
  components: {
    CommentBox,
    Subtask,
    TaskComment,
    TaskActivity,
    Multiselect
  },
  props: {
    task: Object,
    deploymentName: String,
    deploymentId: Number,
    incidentId: Number
  },
  data () {
    return {
      selectOptions: [],
      assignedSelected: [],
      subtaskName: '',
      subtaskAssignedSelected: [],
      isSelectLoading: false,
      isHandlingAssigned: false,
      isHandlingTags: false,
      changeTaskName: '',
      newDescription: '',
      newComment: '',
      tagsSelected: [],
      tagOptions: ['High Priority', 'Medium Priority', 'Low Priority']
    }
  },
  methods: {
    toggle (id, toogleBoolean) {
      this.ApiPut(`subtasks/${id}/status`, { completed: toogleBoolean })
    },
    submitComment (editor) {
      this.ApiPost(`tasks/${this.task.id}/comments`, { text: JSON.stringify(editor.getJSON()) })
      this.$refs.commentBox.resetContent()
    },
    formatSelect: function ({ firstname, surname }) {
      return `${firstname} ${surname}`
    },
    setAssignedSelecter: function () {
      this.assignedSelected = this.task.assignedTo
    },
    openedAssignedDropdown () {
      this.setAssignedSelecter()
    },
    closedAssignedDropdown () {
      if (this.isHandlingAssigned) {
        return
      }
      this.isHandlingAssigned = true // Fix for Bootstrap-vue firing twice.
      if (this.didAssignedChange) {
        this.ApiPut(`tasks/${this.task.id}/assigned`, { users: this.assignedSelected.map(user => user.id) })
          .then(() => { this.isHandlingAssigned = false })
          .catch(() => { this.isHandlingAssigned = false })
      } else {
        this.isHandlingAssigned = false
      }
    },
    openedTaskNameDropdown () {
      this.changeTaskName = this.task.name
    },
    closedTaskNameDropdown () {
      if (this.changeTaskName !== this.task.name) {
        this.ApiPut(`tasks/${this.task.id}/name`, { name: this.changeTaskName })
      }
    },
    addTag (newTag) {
      this.tagOptions.push(newTag)
      this.tagsSelected.push(newTag)
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
    },
    closedTagsDropdown () {
      if (this.isHandlingTags) {
        return
      }
      this.isHandlingTags = true // Fix for Bootstrap-vue firing twice.
      if (this.didTagsChange) {
        this.ApiPut(`tasks/${this.task.id}/tags`, { tags: this.tagsSelected })
          .then(() => { this.isHandlingTags = false })
          .catch(() => { this.isHandlingTags = false })
      } else {
        this.isHandlingTags = false
      }
    },
    deleteTask () {
      this.ApiDelete(`tasks/${this.task.id}`)
        .then(() => {
          this.$emit('close')
        })
    },
    hideDeleteDropdown () {
      this.$refs.DeleteTaskDropdown.hide(true)
    },
    updateDescription () {
      this.ApiPut(`tasks/${this.task.id}/description`, { text: this.newDescription })
    },
    handleSubmit (e) {
      if (!this.subtaskName.length) {
        return
      }
      let subtaskData = { name: this.subtaskName }

      if (this.subtaskAssignedSelected.length) {
        subtaskData.assignedTo = this.subtaskAssignedSelected.map(user => user.id)
      }
      this.ApiPost(`tasks/${this.task.id}/subtasks`, subtaskData)
        .then(() => {
          this.subtaskName = ''
          this.subtaskAssignedSelected = []
          e.target.reset()
        })
    },
    ...mapActions('users', {
      fetchUsers: 'fetchUsers'
    })
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
    },
    didAssignedChange: function () {
      return this.assignedSelected.length !== this.task.assignedTo.length ||
      !this.assignedSelected.every(e => this.task.assignedTo.includes(e))
    },
    didSubtaskAssignedChange: function () {
      return this.subtaskAssignedSelected.length
    },
    didTagsChange: function () {
      return this.tagsSelected.length !== this.task.tags.length ||
      !this.tagsSelected.every(e => this.task.tags.includes(e))
    },
    hasTypedDescription: function () {
      if (this.task.description === this.newDescription) {
        return false
      }
      return true
    },
    ...mapGetters('users', {
      usersIsLoaded: 'isLoaded',
      getUsersGrouped: 'getUsersGrouped'
    })
  },
  created () {
    this.newDescription = this.task.description
    this.tagsSelected = JSON.parse(JSON.stringify(this.task.tags))
    const newTags = this.task.tags.filter(tag => !this.tagOptions.includes(tag))
    for (let tag of newTags) {
      this.tagOptions.push(tag)
    }
    if (this.selectOptions.length || this.isSelectLoading) {
      return
    }
    if (this.usersIsLoaded) {
      this.selectOptions = this.getUsersGrouped
    } else {
      this.isSelectLoading = true
      this.fetchUsers(this.deploymentId)
        .then(() => {
          this.selectOptions = this.getUsersGrouped
          this.isSelectLoading = false
        })
        .catch(() => { this.isSelectLoading = false })
    }
  }
}
</script>
