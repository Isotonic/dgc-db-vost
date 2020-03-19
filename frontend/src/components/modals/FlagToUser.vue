<template>
  <modal :title="'Flag To User'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Flag incident to user">
      <multiselect v-model="selectedUser" :options="selectOptions" :multiple="false" :custom-label="formatSelect" placeholder="Select user to flag to" track-by="id" :closeOnSelect="true" openDirection="bottom" :blockKeys="['Delete']" selectLabel="Select user" deselectLabel="Unselect user" selectedLabel="Selected user" :limit="0" :limitText="() => selectedUser ? `Selected ${selectedUser.firstname} ${selectedUser.surname}` : ''" :loading="isSelectLoading">
        <template slot="singleLabel" slot-scope="{ option }"><strong>{{ option.firstname }} {{ option.surname }}</strong></template>
      </multiselect>
      <textarea-autosize v-model="reason" class="form-control mt-3" placeholder="Add a reason..." required />
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-4">Submit</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Vue from 'vue'
import Multiselect from 'vue-multiselect'
import { mapGetters, mapActions } from 'vuex'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'FlagToUserModal',
  mixins: [ModalMixin],
  components: {
    Multiselect
  },
  props: {
    title: String,
    incidentId: Number,
    deploymentId: Number
  },
  data () {
    return {
      selectedUser: null,
      reason: '',
      selectOptions: [],
      isSelectLoading: false
    }
  },
  methods: {
    handleSubmit (e) {
      if (this.selectedUser && this.reason.length) {
        this.ApiPost(`incidents/${this.incidentId}/flag-to-user`, { id: this.selectedUser.id, reason: this.reason })
          .then(() => {
            this.$emit('close')
            this.reason = ''
            e.target.reset()
            Vue.noty.success(`Successfully flagged to ${this.selectedUser.firstname} ${this.selectedUser.surname}.`)
          })
      }
    },
    formatSelect: function ({ firstname, surname }) {
      return `${firstname} ${surname}`
    },
    ...mapActions('users', {
      fetchUsers: 'fetchUsers'
    })
  },
  computed: {
    ...mapGetters('user', {
      user: 'getUser'
    }),
    ...mapGetters('users', {
      usersIsLoaded: 'isLoaded',
      getUsers: 'getUsers'
    })
  },
  created () {
    if (this.usersIsLoaded) {
      this.selectOptions = this.getUsers.filter(user => user.id !== this.user.id)
    } else {
      this.isSelectLoading = true
      this.fetchUsers(this.deploymentId)
        .then(() => {
          this.selectOptions = this.getUsers.filter(user => user.id !== this.user.id)
          this.isSelectLoading = false
        })
        .catch(() => { this.isSelectLoading = false })
    }
  }
}
</script>
