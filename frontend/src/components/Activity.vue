<template>
  <li>
    <div>
      <i class="fas text-gray-300 fa-1fourx fa-plus-circle activity-icon"></i>
      <div class="media">
        <div>
          <i>
            <img class="media-object rounded-circle" :src="action.user.avatarUrl" alt="Avatar">
          </i>
        </div>
        <div class="media-body">
          {{ action.occurredAt | moment("from", "now") }}
        </div>
        <span class="card-text"><span class="text-primary" v-tooltip="action.user.group? action.user.group.name : 'No Group'">{{ action.user.firstname }} {{ action.user.surname }} </span><v-runtime-template :template="actionText" />.</span>
      </div>
    </div>
  </li>
</template>

<script>
import VRuntimeTemplate from 'v-runtime-template'

/* eslint-disable no-template-curly-in-string */
const fillTemplate = require('es6-dynamic-template')
const actionStrings = {
  'create_incident': 'created incident',
  'create_task': 'created task ${task}',
  'complete_task': 'marked ${task} as complete',
  'delete_task': 'deleted task ${task}',
  'add_comment': 'added an update',
  'delete_comment': 'deleted an update',
  'incomplete_task': 'marked ${task} as incomplete',
  'assigned_user': 'assigned ${targetUsers} to the incident',
  'unassigned_user': 'unassigned ${targetUsers} from the incident',
  'marked_complete': 'marked incident as complete',
  'marked_incomplete': 'marked incident as incomplete',
  'changed_priority': 'changed priority to ${extra}',
  'changed_task_description': 'changed ${task} description to "{$extra}"',
  'assigned_user_task': 'assigned ${targetUsers} to $task',
  'unassigned_user_task': 'unassigned ${targetUsers} from $task',
  'marked_public': 'set the incident to publicly viewable',
  'marked_not_public': 'set the incident to private',
  'complete_subtask': 'marked ${extra} as complete',
  'incomplete_subtask': 'marked ${extra} as incomplete',
  'create_subtask': 'created subtask ${extra}',
  'add_task_comment': 'added comment to ${task}',
  'marked_comment_public': 'marked comment as publicly viewable',
  'marked_comment_not_public': 'marked comment as not publicly viewable',
  'edit_comment': 'edited update',
  'edit_subtask': 'edited subtask ${extra}',
  'edit_incident': 'edited incident details',
  'changed_task_tags': 'changed tags for ${task}',
  'edit_task_comment': 'edited comment in ${task}',
  'delete_task_comment': 'deleted comment in ${task}',
  'delete_subtask': 'deleted subtask in ${task}',
  'change_incident_location': 'changed the incident location',
  'flag_supervisor': 'flagged the incident to a supervisor',
  'request_mark_complete': 'requested the incident be marked as complete',
  'request_mark_incomplete': 'requested the incident be marked as incomplete',
  'edit_incident_name': 'edited incident name from ${extra}',
  'edit_incident_description': 'edited incident description from ${extra}',
  'edit_incident_type': 'changed incident type from ${extra}',
  'edit_incident_reported_via': 'edited incident reported via from ${extra}',
  'edit_incident_linked': 'linked this incident to ${extra}',
  'edit_incident_unlinked': 'unlinked this incident from ${extra}',
  'edit_incident_reference': 'edited incident reference to ${extra}'
}

export default {
  name: 'Activity',
  components: {
    VRuntimeTemplate
  },
  props: {
    action: Object
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
      return `<span>${fillTemplate(actionStrings[this.action.type], { targetUsers: this.action.targetUsers.length ? this.targetedUsersText : null, task: this.action.task, extra: this.action.extra })}</span>`
    }
  }
}
</script>
