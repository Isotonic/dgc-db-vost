<template>
  <select v-model="filterActivities" :class="['custom-select', 'custom-select-sm', 'font-weight-bold', 'ml-2', textBlack ? 'text-black' : 'text-primary']">
    <option value="all">All Activites</option>
    <optgroup label="Incident">
      <option value="create_incident">Created Incidents Only</option>
      <option value="assigned_user">Assigned Users To Incidents Only</option>
      <option value="unassigned_user">Unassigned Users From Incidents Only</option>
      <option value="edit_incident_name">Edited Incident Names Only</option>
      <option value="edit_incident_description">Edited Incident Descriptions Only</option>
      <option value="edit_incident_type">Edited Incident Types Only</option>
      <option value="edit_incident_reported_via">Edited Incident Reported Via Only</option>
      <option value="edit_incident_reference">Edited Incident References Only</option>
      <option value="changed_priority">Changed Incident Priorities Only</option>
      <option value="change_incident_location">Changed Incident Locations Only</option>
      <option value="edit_incident_linked">Incidents Linked Only</option>
      <option value="edit_incident_unlinked">Incidents Unlinked Only</option>
      <option value="marked_public">Marked Incidents Public Only</option>
      <option value="marked_not_public">Marked Incidents Private Only</option>
      <option value="marked_closed">Marked Incidents Complete Only</option>
      <option value="marked_open">Marked Incidents Uncomplete Only</option>
      <option value="flag_supervisor">Incidents Flagged Only</option>
      <option value="request_mark_closed">Incidents Requested Complete Only</option>
      <option value="request_mark_open">Incidents Requested Uncomplete Only</option>
    </optgroup>
    <optgroup label="Task">
      <option value="create_task">Created Tasks Only</option>
      <option value="complete_task">Completed Tasks Only</option>
      <option value="incomplete_task">Uncompleted Tasks Only</option>
      <option value="assigned_user_task">Assigned Users To Tasks Only</option>
      <option value="unassigned_user_task">Unassigned Users From Tasks Only</option>
      <option value="changed_task_description">Changed Task Descriptions Only</option>
      <option value="changed_task_tags">Changed Task Tags Only</option>
      <option value="delete_task">Deleted Tasks Only</option>
      <option value="create_subtask">Created Subtasks Only</option>
      <option value="edit_subtask">Edited Subtasks Only</option>
      <option value="complete_subtask">Completed Subtasks Only</option>
      <option value="incomplete_subtask">Uncompleted Subtasks Only</option>
      <option value="delete_subtask">Deleted Subtasks Only</option>
      <option value="add_task_comment">Added Task Comments Only</option>
      <option value="edit_task_comment">Edited Task Comments Only</option>
      <option value="delete_task_comment">Deleted Task Comments Only</option>
    </optgroup>
    <optgroup label="Update">
      <option value="add_comment">Added Updates Only</option>
      <option value="edit_comment">Edited Updates Only</option>
      <option value="marked_comment_public">Marked Updates Public Only</option>
      <option value="marked_comment_not_public">Marked Updates Private Only</option>
      <option value="delete_comment">Deleted Updates Only</option>
    </optgroup>
  </select>
</template>

<script>
export default {
  name: 'ActvityFilter',
  props: {
    current: {
      type: String,
      default: 'all'
    },
    textBlack: {
      type: Boolean,
      default: false
    }
  },
  data: function () {
    return {
      filterActivities: this.current
    }
  },
  watch: {
    filterActivities (value) {
      this.$emit('changeFilter', value)
    },
    current () {
      this.filterActivities = this.current
    }
  }
}
</script>
