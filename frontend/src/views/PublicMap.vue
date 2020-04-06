<template>
  <div id="wrapper">
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :noSidebar="true" :publicPage="true" :noSearchBar="true" :noMargin="true" />
      <div class="container-fluid py-0 px-0">
        <div class="bg-gradient-primary public-heading">
          <div v-if="deploymentsData.length > 1">
            <h3 class="text-white font-weight-bold py-4 ml-4">Multiple DGVOST Activations</h3>
            <h4 v-for="deployment in deploymentsData" :key="deployment.id" class="text-white font-weight-bold py-2 ml-4">{{ deployment.name }} - {{ deployment.description }}</h4>
          </div>
          <div v-else-if="deploymentsData.length === 1">
            <h3 class="text-white font-weight-bold pt-4 ml-4">DGVOST Active - {{ deploymentsData[0].description }}</h3>
            <h4 class="text-white font-weight-bold py-4 ml-4">{{ deploymentsData[0].description }}</h4>
          </div>
          <div v-else>
            <h3 class="text-white font-weight-bold py-5 ml-4">DGVOST Inactive</h3>
          </div>
        </div>
      </div>
      <div class="container-fluid">
        <div class="row">
          <div class="col-xl-12">
            <div class="card">
              <div class="card-header d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Map</h6>
                  <div>
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
                    <option :value="['comments', 1]">Updates (Asc)</option>/option>
                    <option :value="['comments', -1]">Updates (Desc)</option>/option>
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
                    <incident-card v-for="incident in orderBy(queryResults, sortedBy[0], sortedBy[1])" :key="incident.id" :incident="incident" :publicPage="true" :query="queryDebounced" @goTo="goTo" />
                    <div v-if="!queryResults.length" class="text-center font-weight-bold mt-3">
                    <span v-if="!queryDebounced.length">No incidents</span>
                    <span v-else-if="queryDebounced.length">No incidents found</span>
                    </div>
                  </ul>
                </div>
                <div class="col-lg-9 pl-0">
                  <l-map :zoom="mapSettings.zoom" class="map-container" @click="showBeacon = false" ref="map">
                    <l-tile-layer :url="mapSettings.url" :attribution="mapSettings.attribution"></l-tile-layer>
                    <leaflet-heatmap v-if="heatmap"  @ready="geoMapCenter" :lat-lng="geoToArray" :radius="25" :blur="15" :max="0.01" :key="heatmapKey" />
                    <l-geo-json v-else-if="!heatmap" @ready="geoMapCenter" :geojson="geoJson" :options="geoOptions" ref="geoJsonLayer" />
                    <l-marker v-if="showBeacon && !heatmap" :lat-lng="beacon.coords" :icon="beaconIcon" />
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
import { mapActions } from 'vuex'
import { divIcon, marker, latLng, latLngBounds } from 'leaflet'
import { LMap, LTileLayer, LGeoJson, LMarker } from 'vue2-leaflet'

import router from '@/router/index'
import Topbar from '@/components/Topbar'
import IncidentCard from '@/components/IncidentCard'
import MapPopup from '@/components/MapPopup'

import 'leaflet/dist/leaflet.css'

function fontAwesomeIcon (feature) {
  return divIcon({
    html: `<div class="marker ${feature.properties.open ? 'bg-success' : 'bg-closed'}"><i class="fas fa-${feature.properties.icon} fa-fw text-white fa-2x"></i></div>`,
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
      router,
      propsData: {
        properties: feature.properties,
        publicPage: true
      }
    })
    layer.bindPopup(popup.$mount().$el)
  }
}

export default {
  name: 'publicMap',
  mixins: [Vue2Filters.mixin],
  components: {
    Topbar,
    IncidentCard,
    LeafletHeatmap,
    LMap,
    LTileLayer,
    LGeoJson,
    LMarker
  },
  data () {
    return {
      query: '',
      showingStatus: 'open',
      sortedBy: ['lastUpdatedAt', -1],
      incidentsData: [],
      deploymentsData: [],
      beacon: { coords: [0, 0], open: null },
      showBeacon: false,
      heatmap: false,
      heatmapKey: 0, // Fix to force the heatmap to re-render once the data has changed.
      hasCentered: false,
      mapSettings: {
        url: Vue.prototype.$mapTileServerUrl,
        attribution: `Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors | <a href="${Vue.prototype.$mapTileServerLink}">${Vue.prototype.$mapTileServerName}</a>`,
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
        this.beacon.open = incident.open
        this.showBeacon = true
      }
    },
    geoMapCenter: function () {
      if (!this.hasCentered) {
        const map = this.$refs.map
        let geoJsonLayer = null
        if (this.queryResults.length) {
          if (this.heatmap) {
            let coords = []
            for (let incident of this.queryResults) {
              coords.push(incident.location.geometry.coordinates)
            }
            geoJsonLayer = this.getBounds(coords)
          } else {
            geoJsonLayer = this.$refs.geoJsonLayer.getBounds()
          }
          if (map && geoJsonLayer) {
            map.fitBounds(geoJsonLayer)
            this.hasCentered = true
          }
        } else {
          map.mapObject.setView(latLng(55.019914, -2.592132), 5)
        }
      }
    },
    getBounds: function (coords) {
      const boundingbox = this.calcBoundingCoords(coords)
      return latLngBounds(latLng(boundingbox[1], boundingbox[0]), latLng(boundingbox[3], boundingbox[2]))
    },
    calcBoundingCoords: function (coords) {
      let bounds = [Number.POSITIVE_INFINITY, Number.POSITIVE_INFINITY,
        Number.NEGATIVE_INFINITY, Number.NEGATIVE_INFINITY]
      return coords.reduce(function (prev, coord) {
        return [
          Math.min(coord[0], prev[0]),
          Math.min(coord[1], prev[1]),
          Math.max(coord[0], prev[2]),
          Math.max(coord[1], prev[3])
        ]
      }, bounds)
    },
    getDeploymentsData: function () {
      Vue.prototype.$api
        .get(`public/deployments`)
        .then(r => r.data)
        .then(deployments => {
          this.deploymentsData = deployments
        })
    },
    getIncidentsData: function () {
      Vue.prototype.$api
        .get(`public/incidents`)
        .then(r => r.data)
        .then(incidents => {
          this.incidentsData = incidents
        })
    },
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    })
  },
  computed: {
    queryDebounced: {
      get () {
        return this.query
      },
      set: _.debounce(function (newValue) {
        this.query = newValue
      }, 100)
    },
    incidents: function () {
      if (this.showingStatus === 'open') {
        return this.incidentsData.filter(incident => incident.open)
      } else if (this.showingStatus === 'closed') {
        return this.incidentsData.filter(incident => !incident.open)
      } else {
        return this.incidentsData
      }
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
          comments: incident.comments
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
        html: `<span class="beacon beacon-${this.beacon.open ? 'open' : 'closed'}"></span>`,
        iconSize: [2, 2],
        className: 'beacon-leaflet'
      })
    },
    queryResults: function () {
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
    }
  },
  async created () {
    this.checkUserLoaded(null)
    this.getIncidentsData()
    this.getDeploymentsData()
  }
}
</script>

<style>
.beacon-open.beacon::before,
.beacon-open.beacon::after {
  box-shadow: 0 0 0 3px #02df90;
}

.beacon-closed.beacon::before,
.beacon-closed.beacon::after {
  box-shadow: 0 0 0 3px #95a5a6;
}
</style>
