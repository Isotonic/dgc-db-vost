<template>
  <div class="card shadow">
    <div :class="cardHeaderClass">
      <div :class="['d-flex', !updated ? 'my-2' : '']">
        <h6 class="m-0 font-weight-bold text-light mr-4">{{ properties.name }}</h6>
        <span style="position: absolute;right: 0px;top: 5px;" class="fa-stack fa-2x" v-tooltip="properties.type">
          <i class="far fa-circle fa-stack-2x text-white"></i>
          <i :class="iconClass"></i>
        </span>
      </div>
      <span v-if="updated" class="text-xs text-light mt-1">Last updated {{ properties.lastUpdatedAt | moment("from", "now") }}</span>
    </div>
    <div class="px-3 py-3">
        <p class="card-text my-0"><b>Created:</b> {{ properties.createdAt | moment("Do MMMM YYYY, h:mm A") }}</p>
        <p class="card-text my-1"><b>Description:</b> {{ properties.description }}</p>
        <p class="card-text my-1"><b>Location:</b> {{ properties.address }}</p>
        <p v-if="properties.tasks" class="card-text my-1"><b>Tasks:</b> {{ properties.tasks }}</p>
        <p v-if="properties.comments" class="card-text my-1"><b>Updates:</b> {{ properties.comments }}</p>
        <div class="text-center mt-3">
          <router-link v-if="!publicPage" :to="{ name: 'incident', params: { deploymentName: properties.deploymentName.replace(/ /g, '-'), deploymentId: properties.deploymentId, incidentName: properties.name.replace(/ /g, '-'), incidentId: properties.id }}">
            <a :class="btnClass">Go To Incident</a>
          </router-link>
          <router-link v-else :to="{ name: 'publicIncident', params: { incidentName: properties.name.replace(/ /g, '-'), incidentId: properties.id }}">
            <a :class="btnClass">Go To Incident</a>
          </router-link>
        </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MapPopup',
  props: {
    properties: Object,
    publicPage: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    updated: function () {
      return this.properties.lastUpdatedAt !== this.properties.createdAt
    },
    cardHeaderClass: function () {
      return `card-header bg-${this.properties.open ? 'success' : 'closed'} align-items-center justify-content-between`
    },
    iconClass: function () {
      return `fas fa-${this.properties.icon} float-right text-white fa-stack-1x fa-inverse`
    },
    btnClass: function () {
      return `btn btn-${this.properties.open ? 'success' : 'closed'} text-light`
    }
  }
}
</script>