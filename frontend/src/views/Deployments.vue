<template>
  <div id="wrapper">
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :nosidebar="true" />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 class="font-weight-bold mb-0">Deployments</h1>
          <button class="btn btn-icon-split btn-success mb-1 mt-2" @click="openNewDeploymentModal">
            <span class="btn-icon">
              <i class="fas fa-plus"></i>
            </span>
            <span class="text">New Deployment</span>
          </button>
        </div>
        <deployment-modal v-if="isNewDeploymentModalVisible" v-show="isNewDeploymentModalVisible" :visible="isNewDeploymentModalVisible" :groupOptions="groups" :userOptions="users" @close="isNewDeploymentModalVisible = false" />
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
          <deployment-card v-for="deployment in orderBy(deployments, 'createdAt', -1)" :key="deployment.id" :deployment="deployment" @edit="openEditDeploymentModal" />
        </div>
        <deployment-modal v-if="isEditDeploymentModalVisible" v-show="isEditDeploymentModalVisible" :visible="isEditDeploymentModalVisible" :groupOptions="groups" :userOptions="users" :edit="true" :deployment="editDeployment" @close="isEditDeploymentModalVisible = false" />
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Vue2Filters from 'vue2-filters'
import { mapGetters, mapActions } from 'vuex'

import Topbar from '@/components/Topbar'
import DeploymentCard from '@/components/DeploymentCard'
import DeploymentModal from '@/components/modals/Deployment'

export default {
  name: 'deployments',
  mixins: [Vue2Filters.mixin],
  components: {
    Topbar,
    DeploymentCard,
    DeploymentModal
  },
  data () {
    return {
      users: [],
      groups: [],
      editDeployment: null,
      isNewDeploymentModalVisible: false,
      isEditDeploymentModalVisible: false
    }
  },
  methods: {
    openNewDeploymentModal () {
      if (!this.users.length) {
        this.getUsers()
      }
      if (!this.groups.length) {
        this.getGroups()
      }
      this.isNewDeploymentModalVisible = true
    },
    openEditDeploymentModal (deployment) {
      if (!this.users.length) {
        this.getUsers()
      }
      if (!this.groups.length) {
        this.getGroups()
      }
      this.editDeployment = deployment
      this.isEditDeploymentModalVisible = true
    },
    getUsers () {
      Vue.prototype.$api
        .get(`/users`)
        .then(r => r.data)
        .then(users => {
          this.users = users
        })
    },
    getGroups () {
      Vue.prototype.$api
        .get(`/groups`)
        .then(r => r.data)
        .then(groups => {
          this.groups = groups
        })
    },
    ...mapActions('sockets', {
      checkSocketsConnected: 'checkConnected'
    }),
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    }),
    ...mapActions('deployments', {
      checkDeploymentsLoaded: 'checkLoaded'
    })
  },
  computed: {
    ...mapGetters('sockets', {
      isSocketConnected: 'isConnected'
    }),
    ...mapGetters('deployments', {
      deployments: 'getAll'
    })
  },
  async created () {
    this.checkUserLoaded(null)
    this.checkDeploymentsLoaded()
    this.checkSocketsConnected(null)
  }
}
</script>
