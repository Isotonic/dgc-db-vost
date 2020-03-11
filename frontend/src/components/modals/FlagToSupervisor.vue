<template>
  <modal :title="'Flag To Supervisor'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Flag incident to supervisor">
      <textarea-autosize v-model="reason" class="form-control" placeholder="Add a reason..." required />
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-4">Submit</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Vue from 'vue'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'FlagToSupervisorModal',
  mixins: [ModalMixin],
  props: {
    title: String,
    incidentId: Number
  },
  data () {
    return {
      reason: ''
    }
  },
  methods: {
    handleSubmit (e) {
      if (this.reason.length) {
        this.ApiPost(`incidents/${this.incidentId}/flag-to-supervisor`, { reason: this.reason })
          .then(() => {
            this.$emit('close')
            this.reason = ''
            e.target.reset()
            Vue.noty.success(`Successfully flagged to supervisor.`)
          })
      }
    }
  }
}
</script>
