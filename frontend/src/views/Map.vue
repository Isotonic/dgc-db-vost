<template>
  <div id="wrapper">
    <sidebar :deploymentId="this.deploymentId" :deploymentName="deploymentNameApi" />
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :deploymentId="deploymentId" :deploymentName="deploymentNameApi" />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 v-if="this.deployment" class="font-weight-bold mb-0">{{ this.deployment.name }}</h1>
        </div>
        <div class="row">
          <div class="col-xl-12">
            <div v-if="incidents.length" class="card">
              <div class="card-header d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Map</h6>
                <div class="d-flex">
                  <select v-if="hasPermission('view_all_incidents')" v-model="showingIncidents" class="custom-select custom-select-sm text-primary font-weight-bold">
                    <option value="all">All Incidents</option>
                    <option value="assigned">Assigned Incidents</option>
                  </select>
                  <select v-model="showingStatus" class="custom-select custom-select-sm text-primary font-weight-bold ml-2">
                    <option value="open">Open Only</option>
                    <option value="closed">Closed Only</option>
                    <option value="both">Open and Closed</option>
                  </select>
                  <select v-model="heatmap" class="custom-select custom-select-sm text-primary font-weight-bold ml-2">
                    <option :value="true">Heatmap On</option>
                    <option :value="false">Heatmap Off</option>
                  </select>
                  <select v-model="sortedBy" class="custom-select custom-select-sm text-primary font-weight-bold ml-2">
                    <option :value="['name', 1]">Name (Asc)</option>
                    <option :value="['name', -1]">Name (Desc)</option>
                    <option :value="['priority', 1]">Priority (Asc)</option>
                    <option :value="['priority', -1]">Priority (Desc)</option>
                    <option :value="['tasks', 1]">Tasks (Asc)</option>
                    <option :value="['tasks', -1]">Tasks (Desc)</option>
                    <option :value="['comments', 1]">Comments (Asc)</option>/option>
                    <option :value="['comments', -1]">Comments (Desc)</option>/option>
                    <option :value="['createdAt', 1]">Created At (Asc)</option>/option>
                    <option :value="['createdAt', -1]">Created At (Desc)</option>/option>
                    <option :value="['lastUpdatedAt', 1]">Last Updated (Asc)</option>
                    <option :value="['lastUpdatedAt', -1]">Last Updated (Desc)</option>
                  </select>
                </div>
              </div>
              <div class="row map-height">
                <div class="col-sm-3 overflow-auto pr-0 map-height">
                  <ul class="mb-4 pl-0">
                    <div class="input-group">
                      <div class="input-group-append bl-1">
                        <div class="btn bg-primary">
                          <i class="fas fa-search fa-sm text-white" />
                        </div>
                      </div>
                      <input v-model="queryDebounced" type="text" class="form-control bg-light b-radius-0 small" placeholder="Search for an incident..." aria-label="Search for an incident">
                    </div>
                    <incident-card v-for="incident in orderBy(queryResults, sortedBy[0], sortedBy[1])" :key="incident.id" :incident="incident" :query="queryDebounced" @goTo="goTo" />
                    <div v-if="!queryResults.length" class="text-center font-weight-bold mt-3">
                    <span v-if="!queryDebounced.length">No incidents</span>
                    <span v-else-if="queryDebounced.length">No incidents found</span>
                    </div>
                  </ul>
                </div>
                <div class="col-xl-9 col-lg-9 pl-0">
                  <l-map :zoom="mapSettings.zoom" class="map-container" @click="showBeacon = false" ref="map">
                    <l-tile-layer :url="mapSettings.url" :attribution="mapSettings.attribution"></l-tile-layer>
                    <leaflet-heatmap v-if="heatmap" :lat-lng="geoToArray" :radius="25" :blur="15" :max="0.01" />
                    <l-geo-json v-else-if="!heatmap" @ready="geoMapCenter" :geojson="geoJson" :options="geoOptions" ref="geoJsonLayer" />
                    <l-marker v-if="showBeacon" :lat-lng="beacon.coords" :icon="beaconIcon" />
                  </l-map>
                </div>
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
import _ from 'lodash'
import fz from 'fuzzaldrin-plus'
import LeafletHeatmap from '@/utils/LeafletHeatmap'
import Vue2Filters from 'vue2-filters'
import { mapGetters, mapActions } from 'vuex'
import { divIcon, marker, latLng } from 'leaflet'
import { LMap, LTileLayer, LGeoJson, LMarker } from 'vue2-leaflet'

import router from '@/router/index'
import Topbar from '@/components/Topbar'
import Sidebar from '@/components/Sidebar'
import IncidentCard from '@/components/IncidentCard'
import MapPopup from '@/components/MapPopup'

function fontAwesomeIcon (feature) {
  return divIcon({
    html: `<div class="marker bg-${feature.properties.priority}"><i class="fas fa-${feature.properties.icon} fa-fw text-white fa-2x"></i></div>`,
    iconSize: [2, 2]
  })
}

function isCoordsNull (incident) {
  return incident.location.geometry.coordinates.every(function (v) { return v === null })
}

function onEachFeature (feature, layer) {
  if (feature.properties) {
    const PopupCont = Vue.extend(MapPopup)
    const popup = new PopupCont({
      propsData: {
        properties: feature.properties,
        url: router.resolve({ name: 'incident', params: { deploymentName: feature.properties.deploymentName.replace(/ /g, '-'), deploymentId: feature.properties.deploymentId, incidentName: feature.properties.name.replace(/ /g, '-'), incidentId: feature.properties.id } })
      }
    })
    layer.bindPopup(popup.$mount().$el)
  }
}

function tasksStatus (tasks) {
  if (!tasks.length) {
    return null
  }
  let completedCounter = 0
  for (let value of tasks) {
    if (value.completedAt) {
      completedCounter += 1
    }
  }
  return `${Math.round((completedCounter / tasks.length) * 100)}% (${completedCounter}/${tasks.length})`
}

function commentsStatus (comments) {
  if (!comments.length) {
    return null
  }
  return comments.length.toString()
}

export default {
  name: 'incidentMap',
  mixins: [Vue2Filters.mixin],
  components: {
    Topbar,
    Sidebar,
    IncidentCard,
    LeafletHeatmap,
    LMap,
    LTileLayer,
    LGeoJson,
    LMarker
  },
  props: {
    deploymentName: String,
    deploymentId: Number
  },
  data () {
    return {
      query: '',
      showingStatus: 'open',
      showingIncidents: 'assigned',
      sortedBy: ['lastUpdatedAt', -1],
      beacon: { coords: [0, 0], priority: null },
      showBeacon: false,
      heatmap: false,
      hasCentered: false,
      mapSettings: {
        url: 'https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png',
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors | <a href="https://foundation.wikimedia.org/wiki/Maps_Terms_of_Use">Wikimedia Maps</a>',
        zoom: 15
      }
    }
  },
  methods: {
    goTo: function (incident) {
      const map = this.$refs.map
      const coords = incident.location.geometry.coordinates
      if (map) {
        const flyToLatLng = latLng(coords[1], coords[0])
        map.mapObject.flyTo(flyToLatLng, 15, {
          animate: true,
          duration: 0.5
        })
        this.beacon.coords = [coords[1], coords[0]]
        this.beacon.priority = incident.priority
        this.showBeacon = true
      }
    },
    geoMapCenter: function () {
      if (!this.hasCentered) {
        const map = this.$refs.map
        const geoJsonLayer = this.$refs.geoJsonLayer
        if (map && geoJsonLayer) {
          map.fitBounds(geoJsonLayer.getBounds())
          this.hasCentered = true
        }
      }
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
    incidents: function () {
      let incidents = []
      if (this.showingIncidents === 'assigned') {
        incidents = this.getAssignedIncidents
      } else {
        incidents = this.getIncidents
      }

      if (this.showingStatus === 'open') {
        return incidents.filter(incident => incident.open)
      } else if (this.showingStatus === 'closed') {
        return incidents.filter(incident => !incident.open)
      } else {
        return incidents
      }
    },
    queryDebounced: {
      get () {
        return this.query
      },
      set: _.debounce(function (newValue) {
        this.query = newValue
      }, 100)
    },
    geoToArray: function () {
      let latLngArray = []
      for (let incident of this.queryResults) {
        const coords = incident.location.geometry.coordinates
        if (!isCoordsNull(incident)) {
          latLngArray.push(latLng(coords[1], coords[0]))
        }
      }
      return latLngArray
    },
    geoJson: function () {
      let geo = []
      for (let incident of this.queryResults) {
        const incidentData = {
          id: incident.id,
          name: incident.name,
          description: incident.description,
          priority: incident.priority,
          createdAt: incident.createdAt,
          lastUpdatedAt: incident.lastUpdatedAt,
          type: incident.type,
          icon: incident.icon,
          open: incident.open,
          tasks: tasksStatus(incident.tasks),
          comments: commentsStatus(incident.comments),
          deploymentId: this.deploymentId,
          deploymentName: this.deploymentNameApi
        }
        const propertiesData = { ...incident.location.properties, ...incidentData }
        incident.location.properties = propertiesData
        geo.push(incident.location)
      }
      return geo
    },
    geoOptions () {
      return {
        pointToLayer: function (feature, latlng) {
          return marker(latlng, {
            icon: fontAwesomeIcon(feature)
          })
        },
        onEachFeature: onEachFeature
      }
    },
    beaconIcon: function () {
      return divIcon({
        html: `<span class="beacon beacon-${this.beacon.priority}"></span>`,
        iconSize: [2, 2],
        className: 'beacon-leaflet'
      })
    },
    queryResults () {
      if (!this.query) {
        return this.incidents.filter(incident => !isCoordsNull(incident))
      }
      const preparedQuery = fz.prepareQuery(this.query)
      const scores = {}

      return this.incidents
        .filter(incident => !isCoordsNull(incident))
        .map((incident, index) => {
          const scorableFields = [
            incident.name,
            incident.description,
            incident.location.properties.address
          ].map(toScore => fz.score(toScore, this.query, { preparedQuery }))

          scores[incident.id] = Math.max(...scorableFields)

          return incident
        })
        .filter(option => scores[option.id] > 1)
        .sort((a, b) => scores[b.id] - scores[a.id])
    },
    ...mapGetters('user', {
      hasPermission: 'hasPermission'
    }),
    ...mapGetters('deployments', {
      getDeployment: 'getDeployment'
    }),
    ...mapGetters('incidents', {
      getDeploymentId: 'getDeploymentId',
      getIncidents: 'getIncidents',
      getAssignedIncidents: 'getAssignedIncidents'
    })
  },
  watch: {
    deployment: {
      deep: true,
      handler () {
        if (this.deployment && this.deploymentName !== this.deployment.name) {
          this.deploymentName = this.deployment.name
          history.pushState(null, '', `/deployments/${this.deployment.name.replace(/ /g, '-')}-${this.deploymentId}/incidents`)
        }
      }
    },
    queryDebounced: {
      handler (value) {
        const map = this.$refs.map
        const geoJsonLayer = this.$refs.geoJsonLayer
        if (map && geoJsonLayer) {
          map.fitBounds(geoJsonLayer.getBounds())
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
