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
        <ol v-if="properties.comments.length || (!publicPage && properties.tasks.length)" class="incident-card-actions-list list-unstyled mt-2">
          <li class="incident-card-actions">
            <div v-if="!publicPage && properties.tasks.length" class="mr-1">
              <i class="fas fa-tasks" v-tooltip="'Tasks Complete'"></i>
              <span class="incident-card-actions-text">{{ taskText }}</span>
            </div>
            <div v-if="properties.comments.length">
              <i class="far fa-comment comments-map-popup" v-tooltip="'Updates'"></i>
              <span class="incident-card-actions-text">{{ properties.comments.length }}</span>
            </div>
          </li>
        </ol>
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
      return this.properties.lastUpdatedAt && this.properties.lastUpdatedAt !== this.properties.createdAt
    },
    cardHeaderClass: function () {
      return `card-header ${this.properties.open ? 'bg-success' : 'bg-closed'} align-items-center justify-content-between`
    },
    iconClass: function () {
      return `fas fa-${this.properties.icon} float-right text-white fa-stack-1x fa-inverse`
    },
    btnClass: function () {
      return `btn ${this.properties.open ? 'btn-success' : 'btn-closed'} text-light`
    },
    taskText: function () {
      return `${this.properties.tasks.filter(task => task.completedAt).length}/${this.properties.tasks.length}`
    }
  }
}
</script>
