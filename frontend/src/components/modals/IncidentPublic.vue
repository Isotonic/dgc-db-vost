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
        <social-sharing url="" :title="`[System Generated] ${name}\n${description}\n${getUrl}`" inline-template>
          <network network="twitter">
            <div class="btn btn-icon-split btn-info mt-1 ml-2">
              <span class="btn-icon">
                  <i class="fab fa-twitter"></i>
              </span>
              <span class="text">Twitter</span>
            </div>
          </network>
        </social-sharing>
      </div>
    </form>
  </modal>
</template>

<script>
import router from '@/router/index'
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
      this.ApiPut(`incidents/${this.incident.id}/public`, this.getData)
        .then(() => {
          this.$emit('close')
        })
    }
  },
  computed: {
    checkChanged: function () {
      return this.name !== this.getName || this.description !== this.getDescription
    },
    getName: function () {
      return this.incident.publicName ? this.incident.publicName : this.incident.name
    },
    getDescription: function () {
      return this.incident.publicDescription ? this.incident.publicDescription : this.incident.description
    },
    getUrl: function () {
      return window.location.origin + '/' + router.resolve({ name: 'public incident', params: { incidentName: this.incident.name.replace(/ /g, '-'), incidentId: this.incident.id } }).href
    },
    getData: function () {
      return this.description.length ? { public: true, description: this.description } : { public: true }
    }
  }
}
</script>
