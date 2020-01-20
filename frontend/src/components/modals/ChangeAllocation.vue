<template>
  <Modal :title="'Change Allocation'" @close="close">
    <form aria-label="Change incident allocation">
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
  name: 'ChangeAllocationModal',
  components: {
    Modal
  },
  props: {
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
