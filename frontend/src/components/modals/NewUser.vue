<template>
  <modal :title="'New User'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Create new user">
      <div class="form-group mb-4">
        <label for="email" class="text-primary font-weight-bold">An email will be sent to them allowing them to create an account.</label>
        <input v-model="email" id="email" class="form-control" placeholder="Email" type="email" required>
      </div>
      <div class="form-group mb-3">
        <span class="font-weight-bold text-primary mr-2">Group:</span>
        <select v-model="groupId" class="custom-select custom-select-sm font-weight-bold">
          <option :value="null">None</option>
          <option disabled>──────────</option>
          <option v-for="group in orderBy(groups, 'id')" :key="group.id" :value="group.id">{{ group.name }}</option>
        </select>
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary mt-1">Create</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Vue from 'vue'
import Vue2Filters from 'vue2-filters'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'NewUserModal',
  mixins: [ModalMixin, Vue2Filters.mixin],
  props: {
    title: String,
    visible: Boolean,
    groups: Array
  },
  data () {
    return {
      email: '',
      groupId: null
    }
  },
  methods: {
    handleSubmit (e) {
      if (!this.email.length) {
        return
      }
      this.ApiPost('users', this.groupId ? { email: this.email, group: parseInt(this.groupId) } : { email: this.email })
        .then(() => {
          this.$emit('close')
          this.email = ''
          this.groupId = null
          e.target.reset()
          Vue.noty.success(`Successfully sent email registration to user.`)
        })
    }
  }
}
</script>
