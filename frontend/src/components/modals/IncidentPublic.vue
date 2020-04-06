<template>
  <modal :title="edit ? 'Edit Public Incident' : 'Public Incident'" @close="close">
    <form @submit.prevent="handleSubmit" :aria-label="edit ? 'Edit public incident' : 'Mark incident as public'">
      <div class="form-group mb-4">
        <input v-model="name" class="form-control" placeholder="Public name..." type="text" required>
      </div>
      <div class="form-group mb-4">
        <input v-model="description" class="form-control" placeholder="Public description..." type="text" required>
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary mt-1">{{ edit ? 'Save' : 'Submit' }}</button>
      </div>
    </form>
  </modal>
</template>

<script>
import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'IncidentPublic',
  mixins: [ModalMixin],
  props: {
    title: String,
    visible: Boolean,
    incident: Object,
    edit: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      name: this.incident.publicName ? this.incident.publicName : this.incident.name,
      description: this.incident.publicDescription ? this.incident.publicDescription : this.incident.description
    }
  },
  methods: {
    handleSubmit (e) {
      e.preventDefault()
      if (!this.name.length || (this.edit && !this.checkChanged)) {
        return
      }
      let data = { public: true }
      if (this.name !== this.incident.name) {
        data.name = this.name
      }
      if (this.description !== this.incident.description) {
        data.description = this.description
      }
      this.ApiPut(`incidents/${this.incident.id}/public`, data)
        .then(() => {
          this.$emit('close')
        })
    }
  },
  computed: {
    checkChanged: function () {
      return this.name !== this.getName || this.description !== this.getDescription
    }
  }
}
</script>
