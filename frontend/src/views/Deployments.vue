<template>
  <div>
    <div id="wrapper">
      <div id="content-wrapper" class="d-flex flex-column">
        <topbar :nosidebar="true" />
        <div class="container-fluid">
          <div class="d-sm-flex align-items-center justify-content-between mb-4">
            <h1 class="h3 mb-0">Deployments</h1>
            <button class="btn btn-icon-split btn-success mb-1 mt-2" @click="isNewDeploymentModalVisible = true">
              <span class="btn-icon">
                <i class="fas fa-plus"></i>
              </span>
              <span class="text">New Deployment</span>
            </button>
          </div>
          <new-deployment-modal v-show="isNewDeploymentModalVisible" :visible="isNewDeploymentModalVisible" @close="isNewDeploymentModalVisible = false" />
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
            <deployment-card v-for="deployment in orderBy(deployments, 'createdAt', -1)" :key="deployment.id" :deployment="deployment" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue2Filters from 'vue2-filters'
import { mapGetters, mapActions } from 'vuex'

import Topbar from '@/components/Topbar.vue'
import DeploymentCard from '@/components/DeploymentCard.vue'
import NewDeploymentModal from '@/components/modals/NewDeployment.vue'

export default {
  name: 'deployments',
  mixins: [Vue2Filters.mixin],
  components: {
    Topbar,
    DeploymentCard,
    NewDeploymentModal
  },
  data () {
    return {
      isNewDeploymentModalVisible: false
    }
  },
  methods: {
    openModal (modal) {
      modal = true
    },
    closeModal (modal) {
      modal = false
    },
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    }),
    ...mapActions('deployments', {
      checkDeploymentsLoaded: 'checkLoaded'
    })
  },
  computed: {
    ...mapGetters('deployments', {
      deployments: 'getAll'
    })
  },
  async created () {
    this.checkUserLoaded()
    this.checkDeploymentsLoaded()
  }
}
</script>
