<template>
  <div id="wrapper">
    <sidebar :title="deployment.name"></sidebar>
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 class="h3 mb-0">{{ deployment.name }}</h1>
          <div>
            <a :class="['btn', 'btn-icon-split', 'mb-1', 'mt-2', 'mr-2', incident.openStatus ? 'btn-success' : 'btn-info']" href="#" >
                <span class="btn-icon">
                    <i class="fas fa-check"></i>
                </span>
                <span class="text">{{ incident.openStatus ? 'Mark As Complete' : 'Mark As Incomplete' }}</span>
            </a>
            <a href="#flagModal" class="btn btn-icon-split btn-warning mb-1 mt-2 dropdown-toggle" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              <span class="btn-icon">
                <i class="fas fa-flag"></i>
              </span>
              <span class="text">Flag</span>
            </a>
            <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" aria-labelledby="dropdownPriorityMenu">
              <a class="dropdown-item" href="#" type="submit">User</a>
              <a class="dropdown-item" href="#" data-toggle="modal" data-target="#flagToSupervisorModal">Supervisor</a>
            </div>
          </div>
        </div>
        <div class="row">
          <div class="col-xl-3 col-md-6 mb-4">
            <div class="card border-left-primary shadow h-100 py-2">
              <a v-if="hasPermission('change_allocation')" class="incident-cog" href="#" role="button" data-toggle="modal" data-target="#changeAllocationModal">
              <i class="fas fa-cog float-right" data-toggle="tooltip" title="Change Allocation"></i>
              </a>
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
              <a v-if="hasPermission('change_priority')" :class="['incident-cog', 'text-' + incident.priority]" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                  <i class="fas fa-cog float-right" data-toggle="tooltip" title="Change Priority"></i>
              </a>
              <div class="dropdown-menu dropdown-menu-right shadow animated--fade-in" aria-labelledby="dropdownPriorityMenu">
                <a :class="['dropdown-item', incident.priority === 'Standard' ? 'active' : '']" href="#" type="submit">Standard</a>
                <a :class="['dropdown-item', incident.priority === 'Prompt' ? 'active' : '']" href="#" type="submit">Prompt</a>
                <a :class="['dropdown-item', incident.priority === 'Immediate' ? 'active' : '']" href="#" type="submit">Immediate</a>
              </div>
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
                  <i class="fas fa-cog" data-toggle="tooltip" title="Edit Incident Overview"></i>
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
                  <i class="fas fa-plus" data-toggle="tooltip" title="Add Task"></i>
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
                <a class="text-success" href="#" role="button" data-toggle="modal" data-target="#addCommentModal">
                  <i class="fas fa-plus" data-toggle="tooltip" title="Add Comment"></i>
                </a>
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
import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'
import L from 'leaflet'

import Topbar from '@/components/Topbar.vue'
import Sidebar from '@/components/Sidebar.vue'
import Task from '@/components/Task.vue'
import Comment from '@/components/Comment.vue'
import Activity from '@/components/Activity.vue'

// Fix for markers not loading.
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png')
})

export default {
  name: 'viewIncident',
  components: {
    Topbar,
    Sidebar,
    Task,
    Comment,
    Activity,
    LMap,
    LTileLayer,
    LMarker
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
        'priority': 'Standard',
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
      }
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
