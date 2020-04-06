<template>
  <multiselect v-model="selected" :options="selectOptions" :multiple="true" group-values="users" group-label="name" :group-select="true" placeholder="Type to search" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} users assigned.`" :blockKeys="['Delete']" selectedLabel="Assigned" :loading="isSelectLoading">
    <template v-if="didChange" slot="clear">
      <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setAllocatedSelecter"></div>
    </template>
    <span slot="noResult">Oops! No user found.</span>
  </multiselect>
</template>

<script>
import Vue from 'vue'
import Multiselect from 'vue-multiselect'

export default {
  name: 'MultiSelect',
  components: {
    Multiselect
  },
  props: {
    selected: Object,
    selectOptions: Object,
    alreadySelected: Object,
    isSelectLoading: Boolean
  },
  methods: {
    formatSelect: function ({ firstname, surname }) {
      return `${firstname} ${surname}`
    },
    setSelecter: function () {
      this.selected = this.alreadySelected
    }
  },
  computed: {
    didChange: function () {
      return this.selected.length !== this.alreadySelected.length ||
      !this.selected.every(e => this.alreadySelected.includes(e))
    }
  },
  created () {
    this.setSelecter()
    if (this.selectOptions.length) {
      return
    }
    this.isSelectLoading = true
    Vue.prototype.$api
      .get('groups')
      .then(r => r.data)
      .then(data => {
        this.selectOptions = data
        const noGroupUsers = this.getDeploymentUsers.filter(user => !user.group)
        if (noGroupUsers) {
          this.selectOptions.push({ name: 'No Group', users: [noGroupUsers] })
        }
      })
      .catch(error => {
        Vue.noty.error(error.response.data.message)
      })
    this.isSelectLoading = false
  }
}
</script>
