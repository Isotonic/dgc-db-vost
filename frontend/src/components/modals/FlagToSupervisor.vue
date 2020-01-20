<template>
  <Modal :title="'Flag To Supervisor'" @close="close">
    <form aria-label="Flag incident to supervisor">
      <textarea class="form-control" rows="3" name="reason" placeholder="Add a reason..." required></textarea>
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-4">Submit</button>
      </div>
    </form>
  </Modal>
</template>

<script>
import Modal from '@/components/utils/Modal.vue'

export default {
  name: 'FlagToSupervisorModal',
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
  },
  watch: {
    visible: function () {
      if (this.visible) {
        document.body.classList.add('modal-open')
        return
      }
      document.body.classList.remove('modal-open')
    }
  },
  created: function () {
    if (this.visible) {
      document.body.classList.add('modal-open')
    }
  }
}
</script>
