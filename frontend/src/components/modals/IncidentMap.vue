<template>
  <modal :title="'New Incident'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Add a new incident">
      <div id="Map" class="map-container">
        <MglMap :accessToken="accessToken" :mapStyle="mapStyle" @click="onClickMap" ref="map">
          <MglGeocoderControl :accessToken="accessToken" :input="searchResult" @result="handleResult" :draggable="true" />
          <MglMarker :coordinates="location" :draggable="true" color="blue" ref="marker" />
        </MglMap>
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-4">Submit</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Vue from 'vue'
import 'mapbox-gl/dist/mapbox-gl.css'
import '@mapbox/mapbox-gl-geocoder/dist/mapbox-gl-geocoder.css'
import { MglMap, MglMarker } from 'vue-mapbox'
import MglGeocoderControl from '@/utils/geocoderControl'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'IncidetMap',
  mixins: [ModalMixin],
  components: {
    MglMap,
    MglMarker,
    MglGeocoderControl
  },
  props: {
    incidentId: Number,
    currentLocation: Array
  },
  data () {
    return {
      markerSet: false,
      location: JSON.parse(JSON.stringify(this.currentLocation)),
      accessToken: Vue.prototype.$mapBoxApiKey,
      mapStyle: 'mapbox://styles/mapbox/streets-v11',
      searchResult: ''
    }
  },
  methods: {
    handleSubmit () {
      if (!this.location === this.currentLocation) {
        this.$emit('close')
        document.body.classList.remove('modal-open')
        return
      }
      this.ApiPost(`incidents/${this.incidentId}/location`, { longitude: this.location[0], latitude: this.location[1] })
        .then(() => {
          this.$emit('close')
          document.body.classList.remove('modal-open')
        })
    },
    handleResult (event) {
      this.location = event.result.geometry.coordinates
      this.address = event.result.place_name
      this.markerSet = true
    },
    onClickMap (event) {
      if (this.markerSet) {
        this.location[0] = event.mapboxEvent.lngLat.lng
        this.location[1] = event.mapboxEvent.lngLat.lat
        this.$refs.marker.coordinates = this.location
      } else {
        this.markerSet = true
        this.location[0] = event.mapboxEvent.lngLat.lng
        this.location[1] = event.mapboxEvent.lngLat.lat
      }
    }
  }
}
</script>
