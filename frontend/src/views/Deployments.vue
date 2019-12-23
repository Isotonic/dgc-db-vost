<template>
  <div>
    <div id="wrapper">
      <div id="content-wrapper" class="d-flex flex-column">
        <topbar :nosidebar="true"></topbar>
        <div class="container-fluid">
          <div class="d-sm-flex align-items-center justify-content-between mb-4">
            <h1 class="h3 mb-0">Deployments</h1>
            <a href="#newDeploymentModal" data-toggle="modal" data-target="#newDeploymentModal" class="btn btn-icon-split btn-success mb-1 mt-2">
              <span class="btn-icon">
                <i class="fas fa-plus"></i>
              </span>
              <span class="text">New Deployment</span>
            </a>
          </div>
          <div class="row">
            <div class="col-xl-12 col-lg-10">
              <div class="card shadow mb-4">
                <div class="card-header d-flex align-items-center justify-content-between">
                  <h6 class="font-weight-bold text-primary">Virtual Operations Support Team</h6>
                </div>
                <div class="card-body">
                  <p class="font-weight-bold">This system is designed to ensure responding organisations can build shared situational awareness during multi-angency major or critical incidents.</p>
                  <p>Shared Situational Awareness is achieved by sharing information and understandment of the circumstances between the involved organisations to build a stronger, multi-dimensional understanding of events, their implications, associated risks and potential outcomes. Responders cannot assume other emergency service personnel see things or say things in the same way they and a sustained effort is required to reach common view a common view and understanding of events, risk and their implications.</p>
                  <p>Achieving shared situational awareness is essential for effective interoperability.</p>
                </div>
              </div>
            </div>
          </div>
          <div class="row">
            <deployment-card v-for="deployment in deployments" :key="deployment.id" :deployment="deployment"></deployment-card>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Topbar from '../components/Topbar.vue'
import DeploymentCard from '../components/DeploymentCard.vue'

export default {
  name: 'deployments',
  components: {
    Topbar,
    DeploymentCard
  },
  data () {
    return {
      deployments: [
        { 'id': 1, 'name': 'Storm Test', 'description': 'Hmmm', 'createdAt': '2019-12-12 10:08:08.033814', 'openStatus': true },
        { 'id': 2, 'name': 'Storm Test', 'description': 'Hmmm', 'createdAt': '2019-12-12 10:08:08.033814', 'openStatus': true }
      ]
    }
  }
}
</script>
