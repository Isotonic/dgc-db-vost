<template>
  <div>
    <div v-for="comment in incident.comments" :key="comment.id">
      <public-comment :comment="comment"></public-comment>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

import PublicComment from '@/components/PublicComment'

export default {
  name: 'publicIncident',
  components: {
    PublicComment
  },
  props: {
    incidentName: String,
    incidentId: Number
  },
  data () {
    return {
      incidentData: null
    }
  },
  methods: {
    getIncident: function () {
      Vue.prototype.$http
        .get(`public/incidents/${this.incidentId}`)
        .then(r => r.data)
        .then(incident => {
          this.incidentData = incident
        })
        .catch(error => {
          console.log(error)
        })
    }
  },
  computed: {
    incident: function () {
      if (this.incidentData) {
        return this.incidentData
      }
      this.getIncident()
      return this.incidentData
    },
    parseText: function () {
      try {
        return JSON.parse(this.comment.text)
      } catch (_) {
        return this.comment.text
      }
    }
  }
}
</script>
