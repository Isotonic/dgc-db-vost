<template>
  <div>
    <input :checked="checked" class="mr-2" :id="text" type="checkbox" @change="change">
    <label :for="text" :class="['hover', checked ? 'text-primary' : '']">{{ text }}</label>
    <span  class="text-xs ml-1">- {{ extra }}</span>
  </div>
</template>

<script>
export default {
  name: 'Checkbox',
  props: {
    value: Boolean,
    text: String,
    extra: String
  },
  data: function () {
    return {
      checked: this.value
    }
  },
  methods: {
    change: function () {
      this.checked = !this.checked
      this.$emit('input', this.checked)
    }
  }
}
</script>
