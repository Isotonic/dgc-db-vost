<template>
  <div id="wrapper">
    <sidebar :deploymentId="deploymentId" :deploymentName="deploymentNameApi"/>
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 class="h3 mb-0">{{ deploymentNameApi }}</h1>
          <div class="d-flex mb-1 mt-2">
            <button v-if="incident" :class="['btn', 'btn-icon-split', 'mr-2', incident.open ? 'btn-success' : 'btn-info']" @click="markAsComplete">
                <span class="btn-icon">
                    <i class="fas fa-check"></i>
                </span>
                <span v-if="incident" class="text">{{ incident.open ? 'Mark As Complete' : 'Mark As Incomplete' }}</span>
            </button>
            <b-dropdown id="FlagDropdown" toggle-class="btn-icon-split btn-warning dropdown-toggle text-white">
              <template slot="button-content">
                  <span class="btn-icon">
                    <i class="fas fa-flag"></i>
                  </span>
                  <span class="text">Flag</span>
              </template>
              <b-dropdown-item>User</b-dropdown-item>
              <b-dropdown-item @click="isFlagToSupervisorModalVisible = true">Supervisor</b-dropdown-item>
            </b-dropdown>
            <flag-to-supervisor-modal v-show="isFlagToSupervisorModalVisible" :visible="isFlagToSupervisorModalVisible" @close="isFlagToSupervisorModalVisible = false" />
          </div>
        </div>
        <div class="row">
          <div class="col-xl-3 col-md-6 mb-4">
            <div v-if="!incident" class="card border-left-primary shadow h-100 py-2">
              <vcl-list />
            </div>
            <div v-else class="card border-left-primary shadow h-100 py-2">
              <b-dropdown id="ChangeAllocationDropdown" v-if="hasPermission('change_allocation')" size="xs" right menu-class="mt-3 width-110" variant="link" toggle-tag="a" @show="openedAllocationDropdown" @hide="closedAllocationDropdown">
                <template slot="button-content">
                  <a class="fas fa-cog incident-cog float-right" aria-haspopup="true" v-tooltip="'Change Priority'"></a>
                </template>
                <h6 class="text-primary text-center font-weight-bold">Change Allocation</h6>
                <b-dropdown-divider />
                <div class="pl-1 pr-1">
                  <multiselect v-model="allocatedSelected" :options="selectOptions" :multiple="true" group-values="users" group-label="name" :group-select="true" placeholder="Type to search" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => `${count} users assigned.`" :blockKeys="['Delete']" selectedLabel="Assigned" :loading="isSelectLoading">
                    <template v-if="didAllocatedChange" slot="clear">
                      <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setAllocatedSelecter"></div>
                    </template>
                    <span slot="noResult">Oops! No user found.</span>
                  </multiselect>
                </div>
              </b-dropdown>
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div class="text-s font-weight-bold text-primary text-uppercase mb-1">Assigned To</div>
                    <div class="avatar-group">
                      <a v-for="user in incident.assignedTo" :key="user.name" href="#" class="avatar avatar-sm" v-tooltip="`${user.firstname} ${user.surname}`">
                        <img alt="Avatar" :src="user.avatarUrl" class="rounded-circle avatar-sm">
                      </a>
                    </div>
                    <div v-if="!incident.assignedTo.length" class="h5 mb-0 font-weight-bold text-gray-800">Unassigned</div>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-primary text-white rounded-circle shadow">
                      <i class="fas fa-users fa-1fourx"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-md-6 mb-4">
            <div v-if="!incident" class="card border-left-primary shadow h-100 py-2">
              <vcl-list />
            </div>
            <div v-else :class="['card', 'shadow', 'h-100', 'py-2', 'border-left-' + incident.priority]">
              <b-dropdown id="ChangePriorityDropdown" v-if="hasPermission('change_priority')" size="xs" right menu-class="mt-3" variant="link" toggle-tag="a">
                <template slot="button-content">
                  <a :class="['fas', 'fa-cog', 'incident-cog', 'float-right', 'text-' + incident.priority]" aria-haspopup="true" v-tooltip="'Change Priority'"></a>
                </template>
                <b-dropdown-item id="PriorityStandard" :class="[incident.priority === 'Standard' ? 'active' : '']" @click="changePriority('Standard')">Standard</b-dropdown-item>
                <b-dropdown-item id="PriorityPrompt" :class="[incident.priority === 'Prompt' ? 'active' : '']" @click="changePriority('Prompt')">Prompt</b-dropdown-item>
                <b-dropdown-item id="PriorityImmediate" :class="[incident.priority === 'Immediate' ? 'active' : '']" @click="changePriority('Immediate')">Immediate</b-dropdown-item>
              </b-dropdown>
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div :class="['text-s', 'font-weight-bold',  'text-uppercase', 'mb-1', 'text-' + incident.priority]">Priority</div>
                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{ incident.priority }}</div>
                  </div>
                  <div class="col-auto">
                    <div :class="['icon', 'icon-shape', 'text-white', 'rounded-circle', 'shadow', 'bg-' + incident.priority]">
                      <i :class="['fas', 'fa-1fourx', 'fa-'  + incident.icon]"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-if="incident && incident.tasks.length" class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-success shadow h-100 py-2">
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div class="text-s font-weight-bold text-success text-uppercase mb-1">Tasks</div>
                    <div class="row no-gutters align-items-center">
                      <div class="col-auto">
                        <div class="h5 mb-0 mr-3 font-weight-bold text-gray-800">{{ calculateProgressPercentage }}%</div>
                      </div>
                      <div class="col">
                        <div class="progress progress-sm mr-2">
                          <div :class="['progress-bar', calculateProgressColour]" :style="{ width: calculateProgressPercentage + '%' }" :aria-valuenow="calculateProgressPercentage" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-success text-white rounded-circle shadow">
                      <i class="fas fa-tasks fa-1fourx"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-xl-3 col-md-6 mb-4">
            <div v-if="!incident" class="card border-left-primary shadow h-100 py-2">
              <vcl-list />
            </div>
            <div v-else class="card border-left-info shadow h-100 py-2">
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Last Updated</div>
                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{ incident.lastUpdatedAt | moment("from", "now") }}
                    </div>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-info text-white rounded-circle shadow">
                      <i class="far fa-clock fa-1fourx"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-xl-6 col-lg-7">
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Incident Overview</h6>
                <a href="#" role="button" data-toggle="modal" data-target="#editOverviewModal">
                  <i class="fas fa-cog" v-tooltip="'Edit Incident Overview'"></i>
                </a>
              </div>
              <div v-if="!incident" class="card-body">
                <vcl-facebook />
              </div>
              <div v-else class="card-body">
                <h3 class="font-weight-bold">{{ incident.name }}</h3>
                <p class="card-text"><b>Created:</b> {{ incident.createdAt | moment("Do MMMM YYYY, h:mma") }}</p>
                <p class="card-text"><b>Location:</b> {{ incident.location.properties.address }}</p>
                <p class="card-text"><b>Description:</b> {{ incident.description }}</p>
                <p class="card-text"><b>Reported Via:</b> {{ incident.reportedVia ? incident.reportedVia : 'N/A' }}</p>
                <p class="card-text"><b>Logged by:</b> <a href="#">{{ incident.loggedBy.firstname }} {{ incident.loggedBy.surname }}</a></p>
                <p class="card-text"><b>Reference Number (If Provided):</b> {{ incident.reference ? incident.reference : 'N/A' }}</p>
              </div>
            </div>
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Tasks</h6>
                <a class="text-success" href="#" role="button" data-toggle="modal" data-target="#addTaskModal">
                  <i class="fas fa-plus" v-tooltip="'Add Task'"></i>
                </a>
              </div>
              <div v-if="!incident" class="card-body">
                <vcl-bullet-list :rows="3" />
              </div>
              <ul v-else class="list-group">
                <task v-for="task in orderBy(incident.tasks, 'createdAt')" :key="task.id" :task="task" v-on:openModal="openTaskModal(task)" v-on:toggle="taskToggle"></task>
              </ul>
              <task-modal v-if="task" v-show="isTaskModalVisible" :visible="isTaskModalVisible" @close="isTaskModalVisible = false" :task="task" />
              <div v-if="incident && !incident.tasks.length" class="card-body">
                <p class="card-text text-center">No tasks currently.</p>
              </div>
            </div>
          </div>
          <div class="col-xl-6 col-lg-7">
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Map</h6>
                <div v-if="incident && hasPermission('mark_as_public')" class="custom-switch" data-toggle="tooltip" title="Toggle public visibility">
                  <input type="checkbox" class="custom-control-input" id="PublicToggle" autocomplete="off" :checked="incident.public" @click="togglePublic">
                  <label class="custom-control-label" for="PublicToggle"></label>
                </div>
              </div>
              <div class="card-body">
                <div v-if="!incident">
                  <vcl-facebook />
                </div>
                <l-map v-else :zoom="mapSettings.zoom" :center="incident.location.geometry.coordinates" class="map-container-incident">
                  <l-tile-layer :url="mapSettings.url" :attribution="mapSettings.attribution"></l-tile-layer>
                  <l-marker :lat-lng="incident.location.geometry.coordinates"></l-marker>
                </l-map>
              </div>
            </div>
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Updates</h6>
              </div>
              <div class="card-body bg-light">
                <vcl-bullet-list v-if="!incident" :rows="3" />
                <ul v-else class="list-unstyled">
                  <comment v-for="comment in orderBy(incident.comments, 'sentAt')" :key="comment.id" :comment="comment" :publicIncident="incident.public" @showCommentBox="showCommentBox"></comment>
                </ul>
                <div v-if="incident && !incident.comments.length">
                  <p class="card-text text-center">No updates currently.</p>
                </div>
                <comment-box v-if="incident" v-show="commentBoxVisible" @submitComment="submitComment" ref="commentBox" />
              </div>
              <comment-question-modal v-if="incident" v-show="isCommentQuestionModalVisible" :visible="isCommentQuestionModalVisible" :commentHtml="commentHtml" @btnAction="addComment" @close="isCommentQuestionModalVisible = false">
                <template v-slot:question>
                  <span class="font-weight-bold">Would you like to make this update viewable by the public{{ incident.public ? '?' : ' when the incident is marked public?'}}</span>
                </template>
              </comment-question-modal>
            </div>
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Recent Activity</h6>
              </div>
              <div class="card-body bg-light">
                <vcl-bullet-list v-if="!incident" :rows="3" />
                <ul v-else class="activity">
                  <activity v-for="action in orderBy(incident.activity, 'occurredAt', -1)" :key="action.id" :action="action"></activity>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <file-uploader-modal v-if="isFileUploaderModalVisible" v-show="isFileUploaderModalVisible" :visible="isFileUploaderModalVisible" @close="isFileUploaderModalVisible = false" />
  </div>
</template>

<script>
import Vue from 'vue'
import L from 'leaflet'
import Vue2Filters from 'vue2-filters'
import Multiselect from 'vue-multiselect'
import { mapGetters, mapActions } from 'vuex'
import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'
import { VclList, VclFacebook, VclBulletList } from 'vue-content-loading'

import Topbar from '@/components/Topbar'
import Sidebar from '@/components/Sidebar'
import Task from '@/components/Task'
import Comment from '@/components/Comment'
import Activity from '@/components/Activity'
import CommentBox from '@/components/CommentBox'
import FlagToSupervisorModal from '@/components/modals/FlagToSupervisor'
import TaskModal from '@/components/modals/Task'
import FileUploaderModal from '@/components/modals/FileUploader'
import CommentQuestionModal from '@/components/modals/CommentQuestion'

// Fix for markers not loading.
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

export default {
  name: 'incident',
  mixins: [Vue2Filters.mixin],
  components: {
    Topbar,
    Sidebar,
    Task,
    Comment,
    Activity,
    CommentBox,
    FlagToSupervisorModal,
    TaskModal,
    FileUploaderModal,
    CommentQuestionModal,
    LMap,
    LTileLayer,
    LMarker,
    VclList,
    VclFacebook,
    VclBulletList,
    Multiselect
  },
  props: {
    deploymentName: String,
    deploymentId: Number,
    incidentName: String,
    incidentId: Number
  },
  data () {
    return {
      allocatedSelected: [],
      mapSettings: {
        zoom: 15,
        url: 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png',
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors | <a href="https://foundation.wikimedia.org/wiki/Maps_Terms_of_Use">Wikimedia Maps</a>'
      },
      task: null,
      commentHtml: null,
      commentJson: null,
      selectOptions: [],
      isSelectLoading: false,
      showFlagDropdown: false,
      showPriorityDropdown: false,
      isFlagToSupervisorModalVisible: false,
      isTaskModalVisible: false,
      isFileUploaderModalVisible: false,
      isCommentQuestionModalVisible: false,
      commentBoxVisible: true
    }
  },
  methods: {
    markAsComplete: function () {
      if (this.hasPermission('change_status')) {
        this.ApiPut(`incidents/${this.incidentId}/status`, { open: !this.incident.open })
      }
    },
    changePriority: function (priority) {
      if (this.hasPermission('change_priority')) {
        this.ApiPut(`incidents/${this.incidentId}/priority`, { priority: priority })
      }
    },
    togglePublic: function () {
      if (this.hasPermission('mark_as_public')) {
        this.ApiPut(`incidents/${this.incidentId}/public`, { public: !this.incident.public })
      }
    },
    taskToggle: function (taskId, toggle) {
      this.ApiPut(`tasks/${taskId}/status`, { completed: toggle })
    },
    submitComment (editor) {
      this.commentHtml = editor.getHTML()
      this.commentJson = editor.getJSON()
      this.isCommentQuestionModalVisible = true
    },
    addComment (publicBoolean) {
      this.ApiPost(`incidents/${this.incidentId}/comments`, { text: JSON.stringify(this.commentJson), public: publicBoolean })
      this.isCommentQuestionModalVisible = false
      this.$refs.commentBox.resetContent()
    },
    ApiPut: function (url, data) {
      Vue.prototype.$api
        .put(url, data)
        .then(r => r.data)
        .then(data => {
          Vue.noty.success(data)
        })
        .catch(error => {
          console.log(error.response.data.message)
          Vue.noty.error(error.response.data.message)
        })
    },
    ApiPost: function (url, data) {
      Vue.prototype.$api
        .post(url, data)
        .then(r => r.data)
        .then(data => {
          Vue.noty.success(data)
        })
        .catch(error => {
          console.log(error.response.data.message)
          Vue.noty.error(error.response.data.message)
        })
    },
    openTaskModal: function (task) {
      this.task = task
      this.isTaskModalVisible = true
    },
    openedAllocationDropdown () {
      this.setAllocatedSelecter()
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
          if (noGroupUsers) { // TODO Test
            this.selectOptions.push({ name: 'No Group', users: [noGroupUsers] })
          }
        })
        .catch(error => {
          console.log(error.response.data.message)
          Vue.noty.error(error.response.data.message)
        })
      this.isSelectLoading = false
    },
    closedAllocationDropdown () {
      if (this.didAllocatedChange) {
        this.ApiPut(`incidents/${this.incidentId}/allocation`, { users: this.allocatedSelected.map(user => user.id) })
      }
    },
    formatSelect: function ({ firstname, surname }) {
      return `${firstname} ${surname}`
    },
    setAllocatedSelecter: function () {
      this.allocatedSelected = this.incident.assignedTo
    },
    showCommentBox: function (show) {
      this.commentBoxVisible = show
    },
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    }),
    ...mapActions('deployments', {
      checkDeploymentsLoaded: 'checkLoaded'
    }),
    ...mapActions('incidents', {
      checkIncidentsLoaded: 'checkLoaded'
    })
  },
  computed: {
    deployment: function () {
      return this.getDeployment(this.deploymentId)
    },
    deploymentNameApi: function () {
      if (this.deployment) {
        return this.deployment.name
      }
      return this.deploymentName
    },
    incident: function () {
      return this.getIncident(this.incidentId)
    },
    calculateProgressPercentage: function () {
      if (!this.incident) {
        return 0
      }
      let completedCounter = 0
      for (let value of this.incident.tasks) {
        if (value.completed) {
          completedCounter += 1
        }
      }
      return Math.round((completedCounter / this.incident.tasks.length) * 100)
    },
    calculateProgressColour: function () {
      let percentage = this.calculateProgressPercentage
      return {
        'bg-success': percentage >= 80,
        'bg-orange': percentage >= 50 && percentage < 80,
        'bg-warning': percentage >= 25 && percentage < 50,
        'bg-danger': percentage >= 0 && percentage < 25
      }
    },
    didAllocatedChange: function () {
      return this.allocatedSelected.length !== this.incident.assignedTo.length ||
      !this.allocatedSelected.every(e => this.incident.assignedTo.includes(e))
    },
    ...mapGetters('user', {
      hasPermission: 'hasPermission'
    }),
    ...mapGetters('deployments', {
      getDeployment: 'getDeployment',
      getDeploymentUsers: 'getUsers'
    }),
    ...mapGetters('incidents', {
      getIncident: 'getIncident'
    })
  },
  watch: {
    deployment: {
      deep: true,
      handler () {
        if (this.deployment && this.deploymentName !== this.deployment.name) {
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(' ', '-')}-${this.deploymentId}/incidents`)
        }
      }
    },
    incident: {
      deep: true,
      handler () {
        if (this.incident && this.incidentName !== this.incident.name) {
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(' ', '-')}-${this.deploymentId}/incidents`)
        }
      }
    }
  },
  async created () {
    this.checkUserLoaded()
    this.checkDeploymentsLoaded()
    this.checkIncidentsLoaded(this.deploymentId)
  },
  beforeDestroy () {
    this.editor.destroy()
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
