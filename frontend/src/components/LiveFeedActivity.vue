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
        <span class="card-text">
        <span class="text-primary hover" v-tooltip="action.user.group? action.user.group.name : 'No Group'" @click="openUserModal(action.user.id)">{{ action.user.firstname }} {{ action.user.surname }} </span><v-runtime-template :template="actionText" />.</span>
      </div>
    </div>
  </li>
</template>

<script>
import VRuntimeTemplate from 'v-runtime-template'

/* eslint-disable no-template-curly-in-string */
const fillTemplate = require('es6-dynamic-template')
const actionStrings = {
  'create_incident': 'created incident ${incident}',
  'create_task': 'created task ${task} in ${incident}',
  'complete_task': 'marked ${extra} as complete in ${incident}',
  'delete_task': 'deleted task ${task} in ${incident}',
  'add_comment': 'added an update in ${incident}',
  'delete_comment': 'deleted an update in ${incident}',
  'incomplete_task': 'marked ${extra} as incomplete in ${incident}',
  'assigned_user': 'assigned ${targetUsers} to ${incident}',
  'unassigned_user': 'unassigned ${targetUsers} from ${incident}',
  'marked_complete': 'marked ${incident} as complete',
  'marked_incomplete': 'marked ${incident} as incomplete',
  'changed_priority': 'changed ${incident} priority to ${extra}',
  'changed_task_description': 'changed ${task} description to "{$extra}" in ${incident}',
  'assigned_user_task': 'assigned ${targetUsers} to ${task} in ${incident}',
  'unassigned_user_task': 'unassigned ${targetUsers} from ${task} in ${incident}',
  'marked_public': 'set ${incident} to publicly viewable',
  'marked_not_public': 'set ${incident} to private',
  'complete_subtask': 'marked ${extra} as complete in ${incident}',
  'incomplete_subtask': 'marked ${extra} as incomplete in ${incident}',
  'create_subtask': 'created subtask ${extra} in ${incident}',
  'add_task_comment': 'added comment to ${task} in ${incident}',
  'marked_comment_public': 'marked comment as publicly viewable in ${incident}',
  'marked_comment_not_public': 'marked comment as not publicly viewable in ${incident}',
  'edit_comment': 'edited update in ${incident}',
  'edit_subtask': 'edited subtask ${extra} in ${incident}',
  'edit_incident': 'edited ${incident} details',
  'changed_task_tags': 'changed tags for ${task} in ${incident}',
  'edit_task_comment': 'edited comment in ${task} in ${incident}',
  'delete_task_comment': 'deleted comment in ${task} in ${incident}',
  'delete_subtask': 'deleted subtask in ${task} in ${incident}',
  'change_incident_location': 'changed ${incident} location',
  'flag_supervisor': 'flagged ${incident} to a supervisor',
  'request_mark_complete': 'requested ${incident} be marked as complete',
  'request_mark_incomplete': 'requested ${incident} be marked as incomplete',
  'edit_incident_name': 'edited ${incident} name from ${extra}',
  'edit_incident_description': 'edited ${incident} description from ${extra}',
  'edit_incident_type': 'changed ${incident} type from ${extra}',
  'edit_incident_reported_via': 'edited ${incident} reported via from ${extra}',
  'edit_incident_linked': 'linked ${incident} to #${extra}',
  'edit_incident_unlinked': 'unlinked ${incident} from #${extra}',
  'edit_incident_reference': 'edited ${incident} reference from ${extra}'
}

function slashEscape (contents) {
  return contents
    .replace(/\\/g, '\\\\')
    .replace(/'/g, '&apos')
    .replace(/"/g, '&quot')
    .replace(/\n/g, '<br />')
}

export default {
  name: 'LiveFeedActivity',
  components: {
    VRuntimeTemplate
  },
  props: {
    action: Object,
    deploymentId: Number,
    deploymentName: String
  },
  methods: {
    goToIncident () {
      if (this.$route.params.incidentId && parseInt(this.$route.params.incidentId) === this.action.incidentId) {
        this.$emit('close')
      } else {
        this.$router.push({ name: 'incident', params: { deploymentName: this.deploymentName.replace(/ /g, '-'), deploymentId: this.deploymentId, incidentName: this.action.incidentName.replace(/ /g, '-'), incidentId: this.action.incidentId } })
        this.$emit('close')
      }
    },
    openUserModal (userId) {
      let user = null
      if (this.action.user.id === userId) {
        user = this.action.user
      } else {
        user = this.action.targetUsers.find(user => user.id === userId)
      }
      this.$emit('userModal', user)
    }
  },
  computed: {
    targetedUsersText: function () {
      if (this.action.targetUsers.length === 1) {
        return `<span class="text-primary hover" v-tooltip="'${this.action.targetUsers[0].group ? this.action.targetUsers[0].group.name : 'No Group'}'" @click="openUserModal(${this.action.targetUsers[0].id})">${this.action.targetUsers[0].firstname} ${this.action.targetUsers[0].surname}</span>`
      } else {
        return `${this.action.targetUsers.slice(0, -1).map(user => `<span class="text-primary hover" v-tooltip="'${user.group ? user.group.name : 'No Group'}'">${user.firstname} ${user.surname}</span>`).join(', ')} and <span class="text-primary hover" v-tooltip="'${this.action.targetUsers.slice(-1)[0].group ? this.action.targetUsers.slice(-1)[0].group.name : 'No Group'}'">${this.action.targetUsers.slice(-1)[0].firstname} ${this.action.targetUsers.slice(-1)[0].surname}</span>`
      }
    },
    actionText: function () {
      return `<span>${fillTemplate(actionStrings[this.action.type], { targetUsers: this.action.targetUsers.length ? this.targetedUsersText : null, task: this.action.task, extra: this.action.extra, incident: `<span class="text-primary hover" v-tooltip="{ content: '${this.incidentTooltip}', html: true }" @click="goToIncident">${this.action.incidentName}</span>` })}</span>`
    },
    incidentTooltip: function () {
      return `<span><b>ID:</b> #${this.action.incidentId}<br /><b>Description:</b> ${slashEscape(this.action.description)}<br /><b>Priority:</b> ${slashEscape(this.action.priority)}<br /><b>Location:</b> ${slashEscape(this.action.location)}${this.action.tasks ? `<br /><b>Tasks:<b> ${this.action.tasks}` : ''}${this.action.comments ? `<br /><b>Updates:<b> ${this.action.comments}` : ''}</span>`
    }
  }
}
</script>
