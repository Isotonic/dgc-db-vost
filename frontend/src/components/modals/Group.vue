<template>
  <modal :title="edit ? 'Edit Group' : 'New Group'" @close="close">
    <form @submit.prevent="handleSubmit" :aria-label="edit ? 'Edit group' : 'Create a new group'">
      <div class="form-group mb-4">
        <input v-model="name" class="form-control" placeholder="Group Name" type="text" required>
      </div>
      <div class="form-group mb-3">
        <span class="font-weight-bold text-primary">Permissions:</span>
        <checkbox class="mt-2" v-model="supervisor" :text="'Supervisor'" :extra="'Admin access with full control, inherits all other permissions.'" />
        <checkbox v-model="create_deployment" :text="'Create Deployments'" :extra="'Create new deployments and edit existing ones.'" />
        <checkbox v-model="view_all_incidents" :text="'View All Incidents'" :extra="'View incidents even if not assigned.'" />
        <checkbox v-model="change_priority" :text="'Change Priority'" :extra="'Change an incident\'s priority.'" />
        <checkbox v-model="change_status" :text="'Change Status'" :extra="'Change an incident\'s open status.'" />
        <checkbox v-model="change_allocation" :text="'Change Allocation'" :extra="'Change an incident\'s allocation.'" />
        <checkbox v-model="mark_as_public" :text="'Mark as Public'" :extra="'Change if an incident or update if viewable by the public or not.'" />
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary mt-1">{{ edit ? 'Save' : 'Submit' }}</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Vue from 'vue'

import { ModalMixin } from '@/utils/mixins'
import Checkbox from '@/components/utils/Checkbox'

export default {
  name: 'GroupModal',
  mixins: [ModalMixin],
  components: {
    Checkbox
  },
  props: {
    title: String,
    visible: Boolean,
    group: Object,
    edit: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      name: '',
      supervisor: false,
      create_deployment: false,
      view_all_incidents: false,
      change_priority: false,
      change_status: false,
      change_allocation: false,
      mark_as_public: false
    }
  },
  methods: {
    handleSubmit (e) {
      if (this.edit) {
        this.editGroup()
      } else {
        this.createGroup(e)
      }
    },
    createGroup (e) {
      if (this.name.length) {
        this.ApiPost('groups', this.getData)
          .then(() => {
            this.$emit('close')
            this.supervisor = false
            this.create_deployment = false
            this.view_all_incidents = false
            this.change_priority = false
            this.change_status = false
            this.change_allocation = false
            this.mark_as_public = false
            this.name = ''
            e.target.reset()
            Vue.noty.success(`Successfully created group.`)
          })
      }
    },
    editGroup () {
      if (this.checkChanged) {
        this.ApiPut(`groups/${this.group.id}`, this.getData)
          .then(() => {
            this.$emit('close')
            Vue.noty.success(`Successfully edited group.`)
          })
      }
    }
  },
  computed: {
    checkChanged: function () {
      return !(this.name === this.group.name &&
      this.supervisor === this.group.permissions.includes('supervisor') &&
      this.create_deployment === this.group.permissions.includes('create_deployment') &&
      this.view_all_incidents === this.group.permissions.includes('view_all_incidents') &&
      this.change_priority === this.group.permissions.includes('change_priority') &&
      this.change_status === this.group.permissions.includes('change_status') &&
      this.change_allocation === this.group.permissions.includes('change_allocation') &&
      this.mark_as_public === this.group.permissions.includes('mark_as_public'))
    },
    getData: function () {
      return { name: this.name,
        supervisor: this.supervisor,
        create_deployment: this.create_deployment,
        view_all_incidents: this.view_all_incidents,
        change_priority: this.change_priority,
        change_status: this.change_status,
        change_allocation: this.change_allocation,
        mark_as_public: this.mark_as_public
      }
    }
  },
  created () {
    if (this.edit) {
      this.name = this.group.name
      this.supervisor = this.group.permissions.includes('supervisor')
      this.create_deployment = this.group.permissions.includes('create_deployment')
      this.view_all_incidents = this.group.permissions.includes('view_all_incidents')
      this.change_priority = this.group.permissions.includes('change_priority')
      this.change_status = this.group.permissions.includes('change_status')
      this.change_allocation = this.group.permissions.includes('change_allocation')
      this.mark_as_public = this.group.permissions.includes('mark_as_public')
    }
  }
}
</script>
