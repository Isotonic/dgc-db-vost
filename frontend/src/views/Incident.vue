<template>
  <div id="wrapper">
    <sidebar :title="deployment.name" :deploymentId="deployment.id" :deploymentName="deployment.name"/>
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 class="h3 mb-0">{{ deployment.name }}</h1>
          <div class="d-flex mb-1 mt-2">
            <button :class="['btn', 'btn-icon-split', 'mr-2', incident.openStatus ? 'btn-success' : 'btn-info']">
                <span class="btn-icon">
                    <i class="fas fa-check"></i>
                </span>
                <span class="text">{{ incident.openStatus ? 'Mark As Complete' : 'Mark As Incomplete' }}</span>
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
            <FlagToSupervisorModal v-show="isFlagToSupervisorModalVisible" :visible="isFlagToSupervisorModalVisible" @close="isFlagToSupervisorModalVisible = false" />
          </div>
        </div>
        <div class="row">
          <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-primary shadow h-100 py-2">
              <a v-if="hasPermission('change_allocation')" class="incident-cog" href="#" role="button" @click="isChangeAllocationModalVisible = true">
                <i class="fas fa-cog float-right" v-tooltip="'Change Allocation'"></i>
              </a>
              <ChangeAllocationModal v-show="isChangeAllocationModalVisible" :visible="isChangeAllocationModalVisible" @close="isChangeAllocationModalVisible = false" />
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div class="text-s font-weight-bold text-primary text-uppercase mb-1">Assigned To</div>
                    <div class="avatar-group">
                      <a v-for="user in incident.assignedTo" :key="user.name" href="#" class="avatar avatar-sm" v-tooltip="user.name">
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
            <div :class="['card', 'shadow', 'h-100', 'py-2', 'border-left-' + incident.priority]">
              <b-dropdown id="ChangePriorityDropdown" v-if="hasPermission('change_priority')" size="xs" right menu-class="mt-3" variant="link" toggle-tag="a">
                <template slot="button-content">
                  <a :class="['fas', 'fa-cog', 'incident-cog', 'float-right', 'text-' + incident.priority]" aria-haspopup="true" v-tooltip="'Change Priority'"></a>
                </template>
                <b-dropdown-item id="PriorityStandard" :class="[incident.priority === 'Standard' ? 'active' : '']" href="#" type="submit">Standard</b-dropdown-item>
                <b-dropdown-item id="PriorityPrompt" :class="[incident.priority === 'Prompt' ? 'active' : '']" href="#" type="submit">Prompt</b-dropdown-item>
                <b-dropdown-item id="PriorityImmediate" :class="[incident.priority === 'Immediate' ? 'active' : '']" href="#" type="submit">Immediate</b-dropdown-item>
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
          <div class="col-xl-3 col-md-6 mb-4">
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
            <div class="card border-left-warning shadow h-100 py-2">
              <div class="card-body">
                <div class="row no-gutters align-items-center">
                  <div class="col mr-2">
                    <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Last Updated</div>
                    <div class="h5 mb-0 font-weight-bold text-gray-800">{{ incident.lastUpdated | moment("from", "now") }}
                    </div>
                  </div>
                  <div class="col-auto">
                    <div class="icon icon-shape bg-warning text-white rounded-circle shadow">
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
              <div class="card-body">
                <h3 class="font-weight-bold">{{ incident.name }}</h3>
                <p class="card-text"><b>Created:</b> {{ incident.createdAt | moment("Do MMMM YYYY, h:mma") }}</p>
                <p class="card-text"><b>Location:</b> {{ incident.location }}</p>
                <p class="card-text"><b>Description:</b> {{ incident.description }}</p>
                <p class="card-text"><b>Reported Via:</b> {{ incident.reportedVia }}</p>
                <p class="card-text"><b>Logged by:</b> <a href="#">{{ incident.createdByUser }}</a></p>
                <p class="card-text"><b>Reference Number (If Provided):</b> {{ incident.reference }}</p>
              </div>
            </div>
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Tasks</h6>
                <a class="text-success" href="#" role="button" data-toggle="modal" data-target="#addTaskModal">
                  <i class="fas fa-plus" v-tooltip="'Add Task'"></i>
                </a>
              </div>
              <ul class="list-group">
                <task v-for="task in incident.tasks" :key="task.id" :task="task"></task>
              </ul>
              <div v-if="!incident.tasks.length" class="card-body">
                <p class="card-text text-center">No tasks currently.</p>
              </div>
            </div>
          </div>
          <div class="col-xl-6 col-lg-7">
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Map</h6>
                <div v-if="hasPermission('mark_as_public')" class="custom-switch" data-toggle="tooltip" title="Toggle public visibility">
                  <input type="checkbox" class="custom-control-input" id="PublicToggle" autocomplete="off" :checked="incident.public">
                  <label class="custom-control-label" for="PublicToggle"></label>
                </div>
              </div>
              <div class="card-body">
                <l-map :zoom="mapSettings.zoom" :center="incident.coordinates" class="map-container-incident">
                  <l-tile-layer :url="mapSettings.url" :attribution="mapSettings.attribution"></l-tile-layer>
                  <l-marker :lat-lng="incident.coordinates"></l-marker>
                </l-map>
              </div>
            </div>
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Updates</h6>
                <button class="btn btn-xs text-success" @click="isNewCommentModalVisible = true">
                  <i class="fas fa-plus" v-tooltip="'Add Comment'"></i>
                </button>
                <NewCommentModal v-show="isNewCommentModalVisible" :visible="isNewCommentModalVisible" @close="isNewCommentModalVisible = false" />
              </div>
              <div class="card-body bg-light">
                <ul class="list-unstyled">
                  <comment v-for="comment in incident.comments" :key="comment.id" :comment="comment"></comment>
                </ul>
                <div v-if="!incident.comments.length">
                  <p class="card-text text-center">No updates currently.</p>
                </div>
              </div>
            </div>
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Recent Activity</h6>
              </div>
              <div class="card-body bg-light">
                <ul class="activity">
                  <activity v-for="action in incident.activity" :key="action.id" :action="action"></activity>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'
import L from 'leaflet'
import { DropdownPlugin } from 'bootstrap-vue'

import Topbar from '@/components/Topbar.vue'
import Sidebar from '@/components/Sidebar.vue'
import Task from '@/components/Task.vue'
import Comment from '@/components/Comment.vue'
import Activity from '@/components/Activity.vue'
import FlagToSupervisorModal from '@/components/modals/FlagToSupervisor.vue'
import ChangeAllocationModal from '@/components/modals/ChangeAllocation.vue'
import NewCommentModal from '@/components/modals/NewComment.vue'

Vue.use(DropdownPlugin)

// Fix for markers not loading.
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

export default {
  name: 'incident',
  components: {
    Topbar,
    Sidebar,
    Task,
    Comment,
    Activity,
    LMap,
    LTileLayer,
    LMarker,
    FlagToSupervisorModal,
    ChangeAllocationModal,
    NewCommentModal
  },
  props: {
    deploymentName: String,
    deploymentId: Number,
    incidentName: String,
    incidentId: Number
  },
  data () {
    return {
      user: { 'permissions': ['mark_as_public', 'change_allocation', 'change_priority'] },
      deployment: { 'id': 1, 'name': 'Storm Test', 'description': 'Hmmm', 'createdAt': '2019-12-12 10:08:08.033814', 'openStatus': true },
      incident: {
        'id': 1,
        'pinned': true,
        'name': 'Hmm',
        'description': 'sadasda',
        'reportedVia': '999',
        'location': 'Test',
        'coordinates': [55.872326, -4.288094],
        'createdByUser': 'Test User',
        'priority': 'Prompt',
        'assignedTo': [{ 'name': 'Test User', 'avatarUrl': 'http://c5-dissertation.herokuapp.com/static/img/avatars/24_Jaffer_Naheem.png' }],
        'createdAt': '2019-10-12 10:08:08.033814',
        'lastUpdated': '2019-12-12 10:08:08.033814',
        'openStatus': true,
        'icon': 'exclamation',
        'tasks': [{ 'id': 1, 'name': 'Test', 'createdAt': '2019-10-12 11:08:08.033814', 'completed': true, 'assignedTo': ['Test User', 'Hmm'], 'subtasks': [{ 'completedAt': false }], 'comments': [{ 'name': 'Test User', 'text': 'dasdas' }] }],
        'comments': [{ 'id': 1, 'sentAt': '2019-12-08 11:08:08.033814', 'text': 'dsada', 'user': { 'name': 'Test User', 'avatarUrl': '#' } }],
        'activity': [{ 'user': { 'name': 'Test User', 'avatarUrl': 'http://c5-dissertation.herokuapp.com/static/img/avatars/24_Jaffer_Naheem.png' }, 'occurredAt': '2019-12-03 11:08:08.033814', 'text': 'dsadasd' }] },
      mapSettings: {
        zoom: 15,
        url: 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png',
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors | <a href="https://foundation.wikimedia.org/wiki/Maps_Terms_of_Use">Wikimedia Maps</a>'
      },
      showFlagDropdown: false,
      showPriorityDropdown: false,
      isFlagToSupervisorModalVisible: false,
      isChangeAllocationModalVisible: false,
      isNewCommentModalVisible: false
    }
  },
  methods: {
    hasPermission: function (permission) {
      return this.user.permissions.includes(permission)
    }
  },
  computed: {
    calculateProgressPercentage: function () {
      let completedCounter = 0
      for (let value of this.incident.tasks) {
        if (value.completed) {
          completedCounter += 1
        }
      }
      return (completedCounter / this.incident.tasks.length) * 100
    },
    calculateProgressColour: function () {
      let percentage = this.calculateProgressPercentage
      return {
        'bg-success': percentage >= 80,
        'bg-orange': percentage >= 50 && percentage < 80,
        'bg-warning': percentage >= 25 && percentage < 50,
        'bg-danger': percentage >= 0 && percentage < 25
      }
    }
  }
}
</script>
