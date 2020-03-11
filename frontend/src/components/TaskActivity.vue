<template>
  <li>
    <div>
      <div class="media">
        <div>
          <i>
            <img class="media-object rounded-circle hover" :src="action.user.avatarUrl" alt="Avatar" @click="openUserModal(action.user.id)" />
          </i>
        </div>
        <div class="media-body">
          {{ action.occurredAt | moment("from", "now") }}
        </div>
        <span class="card-text"><span class="text-primary" v-tooltip="action.user.group? action.user.group.name : 'No Group'" @click="openUserModal(action.user.id)">{{ action.user.firstname }} {{ action.user.surname }} </span><v-runtime-template :template="actionText" />.</span>
      </div>
    </div>
    <user-modal v-if="isUserModalVisible" v-show="isUserModalVisible" :visible="isUserModalVisible" :deploymentName="deploymentName" :deploymentId="deploymentId" :currentIncidentId="incidentId" :userProp="userModal" @close="handleUserModalClose" />
  </li>
</template>

<script>
import VRuntimeTemplate from 'v-runtime-template'

import UserModal from './modals/User'

/* eslint-disable no-template-curly-in-string */
const fillTemplate = require('es6-dynamic-template')
const actionStrings = {
  'create_subtask': 'created ${subtask}',
  'complete_subtask': 'marked ${subtask} as complete',
  'delete_subtask': 'deleted ${extra}',
  'changed_description': 'changed task description from ${extra}',
  'assigned_user': 'added ${targetUsers} to task',
  'removed_user': 'removed ${targetUsers} from task',
  'incomplete_subtask': 'marked ${subtask} as incomplete',
  'add_comment': 'added comment to task',
  'edit_subtask': 'edited subtask ${subtask}',
  'changed_tags': 'changed the task\'s tags',
  'edit_task_comment': 'edited task comment',
  'delete_task_comment': 'deleted task comment',
  'complete_task': 'marked ${task} complete',
  'incomplete_task': 'marked ${task} incomplete'
}

export default {
  name: 'TaskActivity',
  components: {
    UserModal,
    VRuntimeTemplate
  },
  props: {
    action: Object,
    deploymentName: String,
    deploymentId: Number,
    incidentId: Number
  },
  data () {
    return {
      userModal: null,
      isUserModalVisible: false
    }
  },
  methods: {
    openUserModal (userId) {
      let user = null
      if (this.action.user.id === userId) {
        user = this.action.user
      } else {
        user = this.action.targetUsers.find(user => user.id === userId)
      }
      this.userModal = user
      this.isUserModalVisible = true
    },
    handleUserModalClose () {
      this.isUserModalVisible = false
      this.$nextTick(() => {
        document.body.classList.add('modal-open')
      })
    }
  },
  computed: {
    targetedUsersText: function () {
      if (this.action.targetUsers.length === 1) {
        return `<span class="text-primary" v-tooltip="'${this.action.targetUsers[0].group ? this.action.targetUsers[0].group.name : 'No Group'}'">${this.action.targetUsers[0].firstname} ${this.action.targetUsers[0].surname}</span>`
      } else {
        return `${this.action.targetUsers.slice(0, -1).map(user => `<span class="text-primary">${user.firstname} ${user.surname}</span>`).join(', ')} and <span class="text-primary">${this.action.targetUsers.slice(-1)[0].firstname} ${this.action.targetUsers.slice(-1)[0].surname}</span>`
      }
    },
    actionText: function () {
      return `<span>${fillTemplate(actionStrings[this.action.type], { targetUsers: this.action.targetUsers.length ? this.targetedUsersText : null, task: this.action.task, subtask: this.action.subtask, extra: this.action.extra })}</span>`
    }
  }
}
</script>
