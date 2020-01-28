<template>
  <modal :title="'Public Update'" @close="close">
    <slot name="question"></slot>
    <div class="editor__content comment-public-text mt-3" v-html="commentHtml" />
    <div class="text-center">
      <button type="submit" class="btn btn-block btn-success mt-3" @click="btnAction(true)">Yes</button>
      <button type="submit" class="btn btn-block btn-danger" @click="btnAction(false)">No</button>
    </div>
  </modal>
</template>

<script>
import Modal from '@/components/utils/Modal'

export default {
  name: 'CommentQuestionModal',
  components: {
    Modal
  },
  props: {
    commentHtml: String,
    visible: Boolean
  },
  methods: {
    btnAction (actionBoolean) {
      this.$emit('btnAction', actionBoolean)
    },
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
