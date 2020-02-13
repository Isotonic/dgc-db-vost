<template>
  <modal :title="'Add Task'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Add a new task">
      <div class="form-group mb-3">
        <input v-model="name" class="form-control" placeholder="Task name" type="text" required>
      </div>
      <div class="form-group mb-3">
        <textarea-autosize v-model="description" class="form-control" placeholder="Description" type="text" />
      </div>
      <div class="form-group mb-4">
        <multiselect v-model="assignedSelected" :options="selectOptions" :multiple="true" group-values="users" group-label="name" :group-select="true" placeholder="Assign users to the task" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} user${count > 1 ? 's' : ''} assigned.`" :blockKeys="['Delete']" selectLabel="" selectGroupLabel="" deselectLabel="" deselectGroupLabel="" selectedLabel="" :loading="isSelectLoading">
          <template v-if="didAssignedChange" slot="clear">
            <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setAssignedSelecter"></div>
          </template>
          <span slot="noResult">Oops! No user found.</span>
        </multiselect>
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary mt-1">Create</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Multiselect from 'vue-multiselect'
import { mapGetters, mapActions } from 'vuex'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'NewTaskModal',
  mixins: [ModalMixin],
  components: {
    Multiselect
  },
  props: {
    title: String,
    visible: Boolean,
    deploymentId: Number,
    incidentId: Number
  },
  data () {
    return {
      name: '',
      description: '',
      selectOptions: [],
      assignedSelected: [],
      isSelectLoading: false
    }
  },
  methods: {
    handleSubmit (e) {
      if (!this.name.length) {
        return
      }
      let taskData = { name: this.name }

      if (this.description.length) {
        taskData.description = this.description
      }
      if (this.assignedSelected.length) {
        taskData.assignedTo = this.assignedSelected.map(user => user.id)
      }
      this.ApiPost(`incidents/${this.incidentId}/tasks`, taskData)
        .then(() => {
          this.$emit('close')
          document.body.classList.remove('modal-open')
          this.name = ''
          this.description = ''
          this.setAssignedSelecter()
          e.target.reset()
        })
    },
    formatSelect: function ({ firstname, surname }) {
      return `${firstname} ${surname}`
    },
    setAssignedSelecter () {
      this.assignedSelected = []
    },
    ...mapActions('users', {
      fetchUsers: 'fetchUsers'
    })
  },
  computed: {
    didAssignedChange: function () {
      return !!this.assignedSelected.length
    },
    ...mapGetters('users', {
      usersIsLoaded: 'isLoaded',
      getUsersGrouped: 'getUsersGrouped'
    })
  },
  created () {
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
