<template>
  <modal :title="'New Incident'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Edit incident location">
      <div class="form-group mb-3">
        <input v-model="address" class="form-control" placeholder="Address" type="text">
      </div>
      <div id="Map" class="map-container">
        <MglMap :accessToken="accessToken" :mapStyle="mapStyle" @click="onClickMap" :center="this.currentLocation" :zoom="15" ref="map">
          <MglGeocoderControl :accessToken="accessToken" :input="searchResult" @result="handleResult" :draggable="true" />
          <MglMarker v-if="markerSet" :coordinates="location" :draggable="true" color="blue" />
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
  name: 'IncidetLocationModal',
  mixins: [ModalMixin],
  components: {
    MglMap,
    MglMarker,
    MglGeocoderControl
  },
  props: {
    incidentId: Number,
    currentAddress: String,
    currentLocation: Array
  },
  data () {
    return {
      markerSet: true,
      address: this.currentAddress,
      location: JSON.parse(JSON.stringify(this.currentLocation)),
      accessToken: Vue.prototype.$mapBoxApiKey,
      mapStyle: 'mapbox://styles/mapbox/streets-v11',
      searchResult: ''
    }
  },
  methods: {
    handleSubmit () {
      if (this.location[0] === this.currentLocation[0] && this.location[1] === this.currentLocation[1] && this.address === this.currentAddress) {
        this.$emit('close')
        document.body.classList.remove('modal-open')
        return
      }
      this.ApiPut(`incidents/${this.incidentId}/location`, { address: this.address, longitude: this.location[0], latitude: this.location[1] })
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
        this.markerSet = false
        this.location[0] = event.mapboxEvent.lngLat.lng
        this.location[1] = event.mapboxEvent.lngLat.lat
        this.$nextTick(() => {
          this.markerSet = true
        })
      } else {
        this.markerSet = true
        this.location[0] = event.mapboxEvent.lngLat.lng
        this.location[1] = event.mapboxEvent.lngLat.lat
      }
    }
  }
}
</script>
