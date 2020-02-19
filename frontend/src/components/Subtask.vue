<template>
  <li :class="['list-group-item', 'list-group-flush', 'subtask', subtask.completed ? 'text-muted' : '']">
      <div class="row align-items-center no-gutters">
          <div class="col mr-2">
              <h6 class="mb-0">
                  <input class="mr-2" type="checkbox" :checked="subtask.completed" @click="toggle">
                  <strong v-if="!edit">{{ subtask.name }} </strong>
                  <input v-else v-model="newName" type="text" required="required" class="form-control-sm was-validated mr-2">
                  <span class="text-xs ml-1">{{ subtaskStatusText }}</span>
              </h6>
              <span v-if="subtask.assignedTo.length && !edit" class="text-xs ml-4">Assigned to {{ assignedToText }}</span>
              <div class="d-flex">
                <multiselect v-if="edit" v-model="assignedSelected" :options="selectOptions" :multiple="true" group-values="users" group-label="name" :group-select="true" placeholder="Type to search" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} users assigned.`" :blockKeys="['Delete']" selectedLabel="Assigned" :loading="isSelectLoading">
                  <template v-if="didAssignedChange" slot="clear">
                    <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setAssignedSelecter"></div>
                  </template>
                  <span slot="noResult">Oops! No user found.</span>
                </multiselect>
                <i v-if="edit" class="fas fa-check hover ml-3 text-black subtask-edit" @click="updateSubtask" v-tooltip="'Update'"></i>
                <i v-if="edit" class="fas fa-times ml-3 text-black subtask-edit" @click="edit = false" v-tooltip="'Cancel'"></i>
              </div>
          </div>
          <div>
            <b-dropdown v-if="!edit" variant="link" size="xs" toggle-tag="div" offset="-1050%">
              <template slot="button-content">
                  <i class="fas fa-ellipsis-v text-black"></i>
              </template>
              <b-dropdown-item @click="setEdit">Edit subtask</b-dropdown-item>
              <b-dropdown-item @click="isQuestionModalVisible = true">Delete subtask</b-dropdown-item>
            </b-dropdown>
            <question-modal v-if="isQuestionModalVisible" v-show="isQuestionModalVisible" :visible="isQuestionModalVisible" :title="'Delete Subtask'" @btnAction="deleteSubtask" @close="isQuestionModalVisible = false">
              <template v-slot:question>
                <div class="text-center">
                  <span class="font-weight-bold text-black">Are you sure you wish to delete this subtask?</span>
                </div>
              </template>
              <template v-slot:body>
              <div class="delete-subtask">
                <h6>
                  <input class="mr-2" type="checkbox" :checked="subtask.completed" :disabled="true">
                  <strong>{{ subtask.name }} </strong><span class="text-xs">{{ subtaskStatusText }}</span>
                </h6>
                <span v-if="subtask.assignedTo.length" class="text-xs ml-4">Assigned to {{ assignedToText }}</span>
              </div>
              </template>
            </question-modal>
          </div>
      </div>
  </li>
</template>

<script>
import Multiselect from 'vue-multiselect'
import { mapGetters, mapActions } from 'vuex'

import QuestionModal from './modals/Question'

export default {
  name: 'Subtask',
  props: {
    subtask: Object,
    deploymentId: Number
  },
  components: {
    QuestionModal,
    Multiselect
  },
  data () {
    return {
      isQuestionModalVisible: false,
      edit: false,
      selectOptions: [],
      assignedSelected: [],
      isSelectLoading: false,
      newName: ''
    }
  },
  methods: {
    toggle: function () {
      event.stopPropagation()
      this.edit = false
      this.$emit('toggle', this.subtask.id, !this.subtask.completed)
    },
    setEdit: function () {
      this.newName = this.subtask.name
      this.setAssignedSelecter()
      this.edit = true
      this.setSelectOptions()
    },
    updateSubtask: function () {
      if (this.newName !== this.subtask.name || this.didAssignedChange) {
        this.ApiPut(`subtasks/${this.subtask.id}`, { name: this.newName, assignedTo: this.assignedSelected.map(user => user.id) })
      }
      this.edit = false
    },
    deleteSubtask: function (modalAnswer) {
      this.isQuestionModalVisible = false
      if (modalAnswer) {
        this.ApiDelete(`subtasks/${this.subtask.id}`)
      }
    },
    formatSelect: function ({ firstname, surname }) {
      return `${firstname} ${surname}`
    },
    setAssignedSelecter: function () {
      this.assignedSelected = this.subtask.assignedTo
    },
    setSelectOptions () {
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
    },
    ...mapActions('users', {
      fetchUsers: 'fetchUsers'
    })
  },
  computed: {
    subtaskStatusText: function () {
      return this.subtask.completed
        ? 'Completed ' + this.$moment.unix(this.subtask.completedAt).fromNow()
        : 'Created ' + this.$moment.unix(this.subtask.createdAt).fromNow()
    },
    assignedToText: function () {
      if (this.subtask.assignedTo.length === 1) {
        return `${this.subtask.assignedTo[0].firstname} ${this.subtask.assignedTo[0].surname}`
      }
      return `${this.subtask.assignedTo.slice(0, -1).map(user => `${user.firstname} ${user.surname}`).join(', ')} and ${this.subtask.assignedTo.slice(-1)[0].firstname} ${this.subtask.assignedTo.slice(-1)[0].surname}`
    },
    didAssignedChange: function () {
      return this.assignedSelected.length !== this.subtask.assignedTo.length ||
      !this.assignedSelected.every(e => this.subtask.assignedTo.includes(e))
    },
    ...mapGetters('users', {
      usersIsLoaded: 'isLoaded',
      getUsersGrouped: 'getUsersGrouped'
    })
  }
}
</script>
