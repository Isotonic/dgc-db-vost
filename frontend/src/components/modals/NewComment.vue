<template>
  <Modal :title="'Add Update'" @close="close">
    <form aria-label="Add an update">
      <div class="form-group mb-3">
        <input class="form-control was-validated" name="comment" placeholder="Write an update..." type="text" required>
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
  name: 'NewCommentModal',
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
