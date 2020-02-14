<template>
  <modal :title="edit ? 'Edit Deployment' : 'New Deployment'" @close="close">
    <form @submit.prevent="handleSubmit" :aria-label="edit ? 'Edit deployment' : 'Create a new deployment'">
      <div class="form-group mb-3">
        <input v-model="name" class="form-control" placeholder="Deployment Name" type="text" required>
      </div>
      <div class="form-group mb-4">
        <input v-model="description" class="form-control" placeholder="Description" type="text" required>
      </div>
      <div v-if="edit" class="form-group mb-4">
        <select v-model="open" class="custom-select custom-select-sm text-primary font-weight-bold full-length">
            <option :value="true"><i class="fas fa-car"></i>Active</option>
            <option :value="false">Deactivated</option><i class="fas fa-subway"></i>
        </select>
      </div>
      <span class="font-weight-bold">Optionally whitelist users and groups, leave both blank to allow everyone access.</span>
      <div class="form-group mb-3 mt-2">
        <multiselect v-model="usersSelected" :options="userOptions" :multiple="true" placeholder="Type to search users" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} user${count > 1 ? 's' : ''} whitelisted.`" :blockKeys="['Delete']" selectLabel="" deselectLabel="" selectedLabel="" :loading="isUserSelectLoading">
          <template v-if="didUsersChange" slot="clear">
            <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setUserSelecter"></div>
          </template>
          <span slot="noResult">Oops! No user found.</span>
        </multiselect>
      </div>
      <div class="form-group mb-4">
        <multiselect v-model="groupsSelected" :options="groupOptions" :multiple="true" placeholder="Type to search groups" track-by="id" label="name" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} group${count > 1 ? 's' : ''} whitelisted.`" :blockKeys="['Delete']" selectLabel="" deselectLabel="" selectedLabel="" :loading="isGroupSelectLoading">
          <template v-if="didGroupsChange" slot="clear">
            <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setGroupSelecter"></div>
          </template>
          <span slot="noResult">Oops! No group found.</span>
        </multiselect>
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-2">{{ edit ? 'Save' : 'Create' }}</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Multiselect from 'vue-multiselect'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'DeploymentModal',
  mixins: [ModalMixin],
  components: {
    Multiselect
  },
  props: {
    title: String,
    visible: Boolean,
    userOptions: Array,
    groupOptions: Array,
    deployment: Object,
    edit: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      name: '',
      description: '',
      open: null,
      usersSelected: [],
      groupsSelected: []
    }
  },
  methods: {
    formatSelect: function ({ firstname, surname }) {
      return `${firstname} ${surname}`
    },
    setUserSelecter: function () {
      if (this.edit) {
        this.usersSelected = this.deployment.users
      } else {
        this.usersSelected = []
      }
    },
    setGroupSelecter: function () {
      if (this.edit) {
        this.groupsSelected = this.deployment.groups
      } else {
        this.groupsSelected = []
      }
    },
    handleSubmit (e) {
      if (!this.name.length || !this.description.length) {
        return
      }
      let deploymentData = { name: this.name, description: this.description }
      if (this.usersSelected.length) {
        deploymentData.users = this.usersSelected.map(user => user.id)
      }
      if (this.groupsSelected.length) {
        deploymentData.groups = this.groupsSelected.map(group => group.id)
      }
      if (this.edit) {
        if (this.name === this.deployment.name && this.description === this.deployment.description && this.open === this.deployment.open && !this.didUsersChange && !this.didGroupsChange) {
          this.$emit('close')
          document.body.classList.remove('modal-open')
        } else {
          deploymentData.open = this.open
          console.log(deploymentData)
          this.ApiPut(`deployments/${this.deployment.id}`, deploymentData)
            .then(() => {
              this.$emit('close')
              document.body.classList.remove('modal-open')
              e.target.reset()
            })
        }
      } else {
        this.ApiPost('deployments', deploymentData)
          .then(() => {
            this.$emit('close')
            document.body.classList.remove('modal-open')
            this.name = ''
            this.description = ''
            this.usersSelected = []
            this.groupsSelected = []
            e.target.reset()
          })
      }
    }
  },
  computed: {
    isUserSelectLoading: function () {
      return !this.userOptions.length
    },
    isGroupSelectLoading: function () {
      return !this.groupOptions.length
    },
    didUsersChange: function () {
      if (this.edit) {
        return this.usersSelected.length &&
        (this.usersSelected.length !== this.deployment.users.length ||
        !this.usersSelected.every(e => this.deployment.users.includes(e)))
      } else {
        return this.usersSelected.length
      }
    },
    didGroupsChange: function () {
      if (this.edit) {
        return this.groupsSelected.length &&
        (this.groupsSelected.length !== this.deployment.groups.length ||
        !this.groupsSelected.every(e => this.deployment.groups.includes(e)))
      } else {
        return this.groupsSelected.length
      }
    }
  },
  created () {
    if (this.edit) {
      this.name = this.deployment.name
      this.description = this.deployment.description
      this.open = this.deployment.open
      this.usersSelected = this.deployment.users
      this.groupsSelected = this.deployment.groups
    }
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
