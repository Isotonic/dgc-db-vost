<template>
  <div id="wrapper">
    <sidebar :deploymentId="deploymentId" :deploymentName="deploymentNameApi"/>
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :deploymentId="deploymentId" :deploymentName="deploymentNameApi" />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 class="font-weight-bold mb-0">{{ deploymentNameApi }} - {{ incidentId }}</h1>
          <div class="d-flex mb-1 mt-2">
            <button v-if="incident" :class="['btn', 'btn-icon-split', 'mr-2', incident.open ? 'btn-success' : 'btn-info']" @click="markAsComplete">
                <span class="btn-icon">
                    <i class="fas fa-check"></i>
                </span>
                <span v-if="incident" class="text">{{ incident.open ? 'Mark As Complete' : 'Mark As Incomplete' }}</span>
            </button>
            <button v-if="incident && !incident.public && hasPermission('mark_as_public')" class="btn btn-icon-split mr-2 btn-success" @click="isIncidentPublicModalVisible = true">
                <span class="btn-icon">
                    <i class="fas fa-eye"></i>
                </span>
                <span class="text">Show To Public</span>
            </button>
            <b-dropdown v-if="incident && incident.public && hasPermission('mark_as_public')" id="FlagDropdown" toggle-class="btn-icon-split btn-info dropdown-toggle text-white mr-2">
              <template slot="button-content">
                  <span class="btn-icon">
                    <i class="fas fa-eye"></i>
                  </span>
                  <span class="text">Public View</span>
              </template>
              <b-dropdown-item :to="{ name: 'public incident', params: { incidentName: this.incidentName.replace(/ /g, '-'), incidentId: this.incidentId }}">View public page</b-dropdown-item>
              <b-dropdown-item @click="isIncidentPublicModalVisible = true">Edit public page</b-dropdown-item>
              <social-sharing url="" :title="`[System Generated] ${getName}\n${getDescription}\n${getUrl}`" inline-template>
                <network network="twitter">
                  <b-dropdown-item>Tweet incident</b-dropdown-item>
                </network>
              </social-sharing>
              <b-dropdown-item @click="changePublic(false)">Hide from public</b-dropdown-item>
            </b-dropdown>
            <incident-public-modal v-if="isIncidentPublicModalVisible" v-show="isIncidentPublicModalVisible" :visible="isIncidentPublicModalVisible" :incident="incident" :edit="incident.public" @close="isIncidentPublicModalVisible = false" />
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
            <flag-to-supervisor-modal v-if="isFlagToSupervisorModalVisible" v-show="isFlagToSupervisorModalVisible" :visible="isFlagToSupervisorModalVisible" @close="isFlagToSupervisorModalVisible = false" />
          </div>
        </div>
        <div class="row">
          <div class="col-xl-3 col-md-6 mb-4">
            <div v-if="!incident" class="card border-left-primary shadow h-100 py-2">
              <vcl-list />
            </div>
            <div v-else class="card border-left-primary shadow h-100 py-2">
              <b-dropdown id="ChangeAllocationDropdown" v-if="hasPermission('change_allocation')" size="xs" right menu-class="mt-3 width-110" variant="link" toggle-tag="a" @shown="openedAllocationDropdown" @hidden="closedAllocationDropdown">
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
                      <i v-for="user in incident.assignedTo" :key="user.name" class="avatar avatar-sm" v-tooltip="`${user.firstname} ${user.surname}`">
                        <img alt="Avatar" :src="user.avatarUrl" class="rounded-circle avatar-sm">
                      </i>
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
            <div v-else-if="incident.lastUpdatedAt !== incident.createdAt" class="card border-left-info shadow h-100 py-2">
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
                <a role="button" @click="isIncidentDetailsModalVisible = true">
                  <i class="fas fa-cog" v-tooltip="'Edit Incident Overview'"></i>
                </a>
              </div>
              <div v-if="!incident" class="card-body">
                <vcl-facebook />
              </div>
              <div v-else class="card-body">
                <h3 class="font-weight-bold">{{ incident.name }}</h3>
                <p class="card-text"><b>Created:</b> {{ incident.createdAt | moment("Do MMMM YYYY, h:mm A") }}</p>
                <p class="card-text"><b>Location:</b> {{ incident.location.properties.address }}</p>
                <p class="card-text"><b>Description:</b> {{ incident.description }}</p>
                <p class="card-text"><b>Reported Via:</b> {{ incident.reportedVia ? incident.reportedVia : 'N/A' }}</p>
                <p class="card-text"><b>Logged by:</b> <span class="text-primary">{{ incident.loggedBy.firstname }} {{ incident.loggedBy.surname }}</span></p>
                <p class="card-text"><b>Reference Number (If Provided):</b> {{ incident.reference ? incident.reference : 'N/A' }}</p>
              </div>
              <incident-details-modal v-if="isIncidentDetailsModalVisible" v-show="isIncidentDetailsModalVisible" :visible="isIncidentDetailsModalVisible" :incident="incident" @close="isIncidentDetailsModalVisible = false" />
            </div>
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Tasks</h6>
                <a class="text-success" role="button" @click="isNewTaskModalVisible = true">
                  <i class="fas fa-plus" v-tooltip="'Add Task'"></i>
                </a>
              </div>
              <new-task-modal v-if="isNewTaskModalVisible" v-show="isNewTaskModalVisible" :visible="isNewTaskModalVisible" :deploymentId="deploymentId" :incidentId="incidentId" @close="isNewTaskModalVisible = false" />
              <div v-if="!incident" class="card-body">
                <vcl-bullet-list :rows="3" />
              </div>
              <ul v-else class="list-group">
                <task v-for="task in orderBy(incident.tasks, 'createdAt')" :key="task.id" :task="task" @openModal="openTaskModal(task)" @toggle="taskToggle"></task>
              </ul>
              <task-modal v-if="isTaskModalVisible" v-show="isTaskModalVisible" :visible="isTaskModalVisible" :deploymentId="this.deploymentId" @close="isTaskModalVisible = false" :task="task" />
              <div v-if="incident && !incident.tasks.length" class="card-body">
                <p class="card-text text-center">No tasks currently.</p>
              </div>
            </div>
          </div>
          <div class="col-xl-6 col-lg-7">
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Map</h6>
              </div>
              <div class="card-body">
                <div v-if="!incident">
                  <vcl-facebook />
                </div>
                <l-map v-else-if="incident.location.geometry.coordinates" :zoom="mapSettings.zoom" :center="mapCoords" class="map-container-incident" ref="map">
                  <l-tile-layer :url="mapSettings.url" :attribution="mapSettings.attribution" />
                  <l-marker @click="flyToCoords" :lat-lng="mapCoords" :icon="fontAwesomeIcon" />
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
                  <comment v-for="comment in orderBy(incident.comments, 'sentAt')" :key="comment.id" :comment="comment" :incident="incident" @showCommentBox="showCommentBox"></comment>
                </ul>
                <div v-if="incident && !incident.comments.length">
                  <p class="card-text text-center">No updates currently.</p>
                </div>
                <comment-box v-if="incident" v-show="commentBoxVisible" @submitComment="submitComment" ref="commentBox" />
              </div>
              <question-modal v-if="isCommentQuestionModalVisible" v-show="isCommentQuestionModalVisible" :visible="isCommentQuestionModalVisible" :title="'Public Update'" @btnAction="addComment" @close="isCommentQuestionModalVisible = false">
                <template v-slot:question>
                  <div class="text-center">
                    <span class="font-weight-bold">Would you like to make this update viewable by the public{{ incident.public ? '?' : ' when the incident is marked public?'}}</span>
                  </div>
                </template>
                <template v-slot:body>
                  <div class="editor__content comment-public-text mt-3" v-html="commentHtml" />
                </template>
              </question-modal>
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
import Vue2Filters from 'vue2-filters'
import Multiselect from 'vue-multiselect'
import { divIcon, latLng } from 'leaflet'
import { mapGetters, mapActions } from 'vuex'
import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'
import { VclList, VclFacebook, VclBulletList } from 'vue-content-loading'

import router from '@/router/index'
import Topbar from '@/components/Topbar'
import Sidebar from '@/components/Sidebar'
import Task from '@/components/Task'
import Comment from '@/components/Comment'
import Activity from '@/components/Activity'
import CommentBox from '@/components/CommentBox'
import FlagToSupervisorModal from '@/components/modals/FlagToSupervisor'
import IncidentPublicModal from '@/components/modals/IncidentPublic'
import IncidentDetailsModal from '@/components/modals/IncidentDetails'
import NewTaskModal from '@/components/modals/NewTask'
import TaskModal from '@/components/modals/Task'
import FileUploaderModal from '@/components/modals/FileUploader'
import QuestionModal from '@/components/modals/Question'

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
    NewTaskModal,
    TaskModal,
    FileUploaderModal,
    IncidentPublicModal,
    IncidentDetailsModal,
    QuestionModal,
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
        url: 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png',
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors | <a href="https://foundation.wikimedia.org/wiki/Maps_Terms_of_Use">Wikimedia Maps</a>',
        zoom: 15
      },
      task: null,
      commentHtml: null,
      commentJson: null,
      selectOptions: [],
      isSelectLoading: false,
      showFlagDropdown: false,
      showPriorityDropdown: false,
      isFlagToSupervisorModalVisible: false,
      isIncidentPublicModalVisible: false,
      isIncidentDetailsModalVisible: false,
      isNewTaskModalVisible: false,
      isTaskModalVisible: false,
      isFileUploaderModalVisible: false,
      isCommentQuestionModalVisible: false,
      commentBoxVisible: true,
      isHandlingAllocation: false
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
    changePublic: function (publicBoolean) {
      if (this.hasPermission('mark_as_public')) {
        this.ApiPut(`incidents/${this.incidentId}/public`, { public: publicBoolean })
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
    openTaskModal: function (task) {
      this.task = task
      this.isTaskModalVisible = true
    },
    openedAllocationDropdown () {
      this.setAllocatedSelecter()
      if (this.selectOptions.length || this.isSelectLoading) {
        return
      }
      if (this.usersIsLoaded) {
        this.selectOptions = this.getUsersGrouped
      } else {
        this.isSelectLoading = true
        this.fetchUsers(this.deploymentId)
          .then(() => {
            this.selectOptions = this.getUsersGrouped
            this.isSelectLoading = false
          })
          .catch(() => { this.isSelectLoading = false })
      }
    },
    closedAllocationDropdown () {
      if (this.isHandlingAllocation) {
        return
      }
      this.isHandlingAllocation = true // Fix for Bootstrap-vue firing twice.
      if (this.didAllocatedChange) {
        this.ApiPut(`incidents/${this.incidentId}/allocation`, { users: this.allocatedSelected.map(user => user.id) })
          .then(() => { this.isHandlingAllocation = false })
      } else {
        this.isHandlingAllocation = false
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
    flyToCoords: function () {
      const map = this.$refs.map
      if (map) {
        const flyToLatLng = latLng(this.mapCoords)
        map.mapObject.flyTo(flyToLatLng, 12, {
          animate: true,
          duration: 0.5
        })
      }
    },
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    }),
    ...mapActions('users', {
      fetchUsers: 'fetchUsers'
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
    mapCoords: function () {
      const reversedCoords = [...this.incident.location.geometry.coordinates].reverse()
      return reversedCoords
    },
    fontAwesomeIcon: function (feature) {
      return divIcon({
        html: `<div class="marker bg-${this.incident.priority}"><i class="fas fa-${this.incident.icon} fa-fw text-white fa-2x"></i></div>`,
        iconSize: [2, 2]
      })
    },
    getName: function () {
      return this.incident.publicName ? this.incident.publicName : this.incident.name
    },
    getDescription: function () {
      return this.incident.publicDescription ? this.incident.publicDescription : this.incident.description
    },
    getUrl: function () {
      return window.location.origin + '/' + router.resolve({ name: 'public incident', params: { incidentName: this.incident.name.replace(/ /g, '-'), incidentId: this.incident.id } }).href
    },
    ...mapGetters('user', {
      hasPermission: 'hasPermission'
    }),
    ...mapGetters('users', {
      usersIsLoaded: 'isLoaded',
      getUsersGrouped: 'getUsersGrouped'
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
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(/ /g, '-')}-${this.deploymentId}/incidents`)
        }
      }
    },
    incident: {
      deep: true,
      handler () {
        if (this.incident && this.incidentName !== this.incident.name) {
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(/ /g, '-')}-${this.deploymentId}/incidents`)
        }
      }
    }
  },
  async created () {
    this.checkUserLoaded()
    this.checkDeploymentsLoaded()
    this.checkIncidentsLoaded(this.deploymentId)
  }
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
