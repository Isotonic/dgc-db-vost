<template>
  <modal :title="'Flag To Supervisor'" @close="close">
    <form aria-label="Flag incident to supervisor">
      <textarea class="form-control" rows="3" name="reason" placeholder="Add a reason..." required></textarea>
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-4">Submit</button>
      </div>
    </form>
  </modal>
</template>

<script>
import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'FlagToSupervisorModal',
  mixins: [ModalMixin],
  props: {
    title: String
  }
}
</script>
