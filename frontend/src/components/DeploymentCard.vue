<template>
  <div class="col-xl-4 col-lg-6">
    <div :class="['card shadow', 'mb-4', deployment.open ? 'border-left-success' : 'border-left-info']">
      <div class="card-header d-flex align-items-center justify-content-between">
        <h6 class="font-weight-bold text-primary">{{ deployment.name }}
          <p class="mb-0 mt-1 text-muted text-xs text-nowrap">Created {{ deployment.createdAt | moment("from", "now") }}</p>
        </h6>
        <div class="dropdown no-arrow">
          <a href="#" role="button" class="dropdown-toggle" @click="$emit('edit', deployment)">
            <i class="fas fa-cog"></i>
          </a>
        </div>
      </div>
      <div class="card-body text-center">
        <p class="font-weight-bold text-left">{{ deployment.description }}</p>
        <router-link :to="{ name: 'incidents', params: { deploymentName: deployment.name.replace(/ /g, '-'), deploymentId: deployment.id }}" :class="['btn', deployment.open ? 'btn-success' : 'btn-info']">View Deployment</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeploymentCard',
  props: {
    deployment: Object
  }
}
</script>
