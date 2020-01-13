<template>
  <transition name="fade">
    <div class="modal" tabindex="-1" role="dialog" aria-labelledby="changeAllocationModal" :aria-hidden="!visible">
      <div class="modal-backdrop" @click="close"/>
      <div class="modal-dialog" role="document">
          <div class="modal-content">
            <div class="modal-body p-0">
              <div class="card shadow">
                <div class="card-header py-3 d-flex align-items-center justify-content-between">
                  <h6 class="m-0 font-weight-bold text-primary">{{ title }}</h6>
                  <button class="close" type="button" data-dismiss="modal" aria-label="Close">
                    <span :aria-hidden="!visible" @click="close">×</span>
                  </button>
                </div>
                <div class="card-body">
                  <slot></slot>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'Modal',
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
