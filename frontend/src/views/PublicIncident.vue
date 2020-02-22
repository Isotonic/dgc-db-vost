<template>
  <div id="wrapper">
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :noSidebar="true" :publicPage="true" :noSearchBar="true" />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 class="font-weight-bold mb-0">{{ incident.deployment }}</h1>
        </div>
        <div class="row">
          <div class="col-xl-6 col-lg-7">
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Incident Overview</h6>
              </div>
              <div class="card-body">
                <h3 class="font-weight-bold">{{ incident.name }}</h3>
                <p class="card-text"><b>Created:</b> {{ incident.createdAt | moment("Do MMMM YYYY, h:mm A") }}</p>
                <p class="card-text"><b>Location:</b> {{ incident.location.properties.address }}</p>
                <p class="card-text"><b>Description:</b> {{ incident.description }}</p>
              </div>
            </div>
            <div v-if="incident.comments.length" class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Updates</h6>
              </div>
              <div class="card-body">
                <ul class="list-unstyled" v-for="comment in incident.comments" :key="comment.id">
                  <public-comment :comment="comment"></public-comment>
                </ul>
              </div>
            </div>
          </div>
          <div class="col-xl-6 col-lg-7">
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Map</h6>
              </div>
              <div class="card-body">
                <l-map :zoom="mapSettings.zoom" :center="mapCoords" class="map-container-incident" ref="map">
                  <l-tile-layer :url="mapSettings.url" :attribution="mapSettings.attribution" />
                  <l-marker @click="flyToCoords" :lat-lng="mapCoords" :icon="fontAwesomeIcon" />
                </l-map>
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
import router from '@/router'
import { divIcon, latLng } from 'leaflet'
import { LMap, LTileLayer, LMarker } from 'vue2-leaflet'

import Topbar from '@/components/Topbar'
import PublicComment from '@/components/PublicComment'

import 'leaflet/dist/leaflet.css'

export default {
  name: 'publicIncident',
  components: {
    Topbar,
    PublicComment,
    LMap,
    LTileLayer,
    LMarker
  },
  props: {
    incidentName: String,
    incidentId: Number
  },
  data () {
    return {
      incidentData: null,
      mapSettings: {
        url: 'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        zoom: 15
      }
    }
  },
  methods: {
    getIncident: function () {
      Vue.prototype.$http
        .get(`public/incident/${this.incidentId}`)
        .then(r => r.data)
        .then(incident => {
          this.incidentData = incident
        })
        .catch(error => {
          console.log(error)
          router.push({ name: 'pageNotFound' })
        })
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
    }
  },
  computed: {
    incident: function () {
      if (this.incidentData) {
        return this.incidentData
      }
      this.getIncident()
      return this.incidentData
    },
    parseText: function () {
      try {
        return JSON.parse(this.comment.text)
      } catch (_) {
        return this.comment.text
      }
    },
    mapCoords: function () {
      const reversedCoords = [...this.incident.location.geometry.coordinates].reverse()
      return reversedCoords
    },
    fontAwesomeIcon: function (feature) {
      return divIcon({
        html: `<div class="marker ${this.incident.open ? 'bg-success' : 'bg-closed'}"><i class="fas fa-${this.incident.icon} fa-fw text-white fa-2x"></i></div>`,
        iconSize: [2, 2]
      })
    }
  }
}
</script>
