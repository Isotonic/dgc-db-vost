<template>
  <modal :title="title" @close="close">
    <slot name="question"></slot>
    <slot name="body"></slot>
    <div class="text-center">
      <button type="submit" class="btn btn-block btn-success mt-3" @click="btnAction(true)">Yes</button>
      <button type="submit" class="btn btn-block btn-danger" @click="btnAction(false)">No</button>
    </div>
  </modal>
</template>

<script>
import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'QuestionModal',
  mixins: [ModalMixin],
  props: {
    title: String
  },
  methods: {
    btnAction (actionBoolean) {
      document.body.classList.remove('modal-open')
      this.$emit('btnAction', actionBoolean)
    }
  }
}
</script>
