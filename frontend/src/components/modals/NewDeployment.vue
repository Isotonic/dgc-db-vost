<template>
  <Modal :title="'New Deployment'" @close="close">
    <form aria-label="Create a new deployment">
      <div class="form-group mb-3">
        <input class="form-control was-validated" name="name" placeholder="Deployment Name" type="text" required>
      </div>
      <div class="form-group mb-3">
        <input class="form-control was-validated" name="description" placeholder="Description" type="text" required>
      </div>
      <div class="form-group mb-3">
      </div>
      <div class="form-group mb-3">
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-4">Submit</button>
      </div>
    </form>
  </Modal>
</template>

<script>
import Modal from '@/components/utils/Modal.vue'

export default {
  name: 'NewDeploymentModal',
  components: {
    Modal
  },
  props: {
    title: String,
    visible: Boolean
  },
  methods: {
    close () {
      this.$emit('close')
    }
  }
}
</script>
