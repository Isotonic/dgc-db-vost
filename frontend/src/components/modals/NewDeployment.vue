<template>
  <modal :title="'New Deployment'" @close="close">
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
  </modal>
</template>

<script>
import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'NewDeploymentModal',
  mixins: [ModalMixin],
  props: {
    title: String,
    visible: Boolean
  }
}
</script>
