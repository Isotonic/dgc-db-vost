<template>
  <modal :title="'Request Status Change'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Request incident status change">
      <textarea-autosize v-model="reason" class="form-control" placeholder="Add a reason (optional)" />
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
      this.ApiPost(`incidents/${this.incidentId}/request-status-change`, this.reason.length ? { reason: this.reason } : {})
        .then(() => {
          this.$emit('close')
          document.body.classList.remove('modal-open')
          this.reason = ''
          e.target.reset()
          Vue.noty.success(`Successfully requested incident status change.`)
        })
    }
  }
}
</script>
