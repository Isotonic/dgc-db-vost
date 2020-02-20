<template>
  <modal :title="'New Incident'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Add a new incident">
      <div class="form-group mb-3">
        <input v-model="name" class="form-control was-validated" placeholder="Incident Name" type="text" required>
      </div>
      <textarea-autosize v-model="description" class="form-control" rows="3" placeholder="Description" required/>
      <div class="form-group my-3">
        <select v-model="type" class="custom-select custom-select-sm full-length">
          <option :value="null" disabled>Select the type of incident</option>
          <optgroup label="Transport Disruption">
            <option value="Road Incident"><i class="fas fa-car"></i> Road Obstruction / Closure / Disruption</option>
            <option value="Rail Incident">Railway Incident / Disruption</option><i class="fas fa-subway"></i>
            <option value="Aviation Incident">Aviation Incident / Disruption</option><i class="fas fa-plane"></i>
            <option value="Maritine Incident">Maritine Incident / Disruption</option><i class="fas fa-ship"></i>
          </optgroup>
          <optgroup label="Severe Weather">
            <option value="Snow / Ice">Snow / Ice</option><i class="fas fa-snowflake"></i>
            <option value="Severe Wind">Severe Wind</option><i class="fas fa-wind"></i>
            <option value="Rain/Flooding">Rain / Flooding</option><i class="fas fa-cloud-showers-heavy"></i>
          </optgroup>
          <optgroup label="General Incident">
            <option value="Industrial">Industrial</option><i class="fas fa-industry"></i>
            <option value="Major Accident Hazard Pipeline">Major Accident Hazard Pipeline</option>
            <option value="Nuclear Incident">Nuclear Incident</option><i class="fas fa-radiation"></i>
            <option value="Fire / Explosion">Fire / Explosion</option><i class="fas fa-fire"></i>
            <option value="Building Collapse">Building Collapse</option><i class="fas fa-building"></i>
            <option value="Reservoir">Reservoir</option>
          </optgroup>
          <optgroup label="Fuel / Utilities">
            <option value="Fuel Disruption">Fuel Disruption</option><i class="fas fa-gas-pump"></i>
            <option value="Power Outage">Power Outage</option><i class="fas fa-plug"></i>
            <option value="Gas Supply Interruption">Gas Supply Interruption</option>
            <option value="Public Water Supply">Public Water Supply</option><i class="fas fa-water"></i>
            <option value="Private Water Supply">Private Water Supply</option><i class="fas fa-water"></i>
            <option value="Telecoms Outage">Telecoms Outage</option><i class="fas fa-phone-slash"></i>
            <option value="Blackstart">Blackstart</option>
          </optgroup>
          <optgroup label="Human Health">
            <option value="Pandemic">Pandemic</option>
            <option value="Food Contamination">Food Contamination</option><i class="fas fa-utensils"></i>
            <option value="Exotic Notification Disease">Exotic Notification Disease</option>
          </optgroup>
          <optgroup label="Crime & Disorder">
            <option value="Terrorism">Terrorism</option>
            <option value="Cyber Attack">Cyber Attack</option>
            <option value="Public Disorder">Public Disorder</option>
            <option value="Protest">Protest</option>
          </optgroup>
          <optgroup label="People">
            <option value="Fatalities">Fatalities</option>
            <option value="Casualties">Casualties</option><i class="fas fa-first-aid"></i>
            <option value="Missing Person(s)">Missing Person(s)</option>
            <option value="Resque Required">Resque Required</option>
            <option value="Evacuation">Evacuation</option>
            <option value="Rest Centre Activation">Rest Centre Activation</option>
            <option value="Survivor Reception Centre Activation">Survivor Reception Centre Activation</option>
            <option value="Friends & Family Reception Centre Activation">Friends & Family Reception Centre Activation</option>
            <option value="Humanitarian Assistance Centre Activation">Humanitarian Assistance Centre Activation</option>
            <option value="Casualty Bureau Activation">Casualty Bureau Activation</option>
            <option value="General Welfare Provision">General Welfare Provision</option>
            <option value="Vaccination">Vaccination</option>
          </optgroup>
          <optgroup label="Communications">
            <option value="Press Release">Press Release</option><i class="fas fa-newspaper"></i>
            <option value="SitRep Required">SitRep Required</option>
            <option value="Social Media">Social Media</option>
            <option value="DGVOST Activation">DGVOST Activation</option>
          </optgroup>
          <optgroup label="Animal Health">
            <option value="Control Zones">Control Zones</option>
            <option value="Surveillance Zones">Surveillance Zones</option><i class="fas fa-video"></i>
            <option value="Movement Restrictions">Movement Restrictions</option>
            <option value="Cull">Cull</option>
            <option value="Disposal">Disposal</option>
            <option value="Disinfection">Disinfection</option>
            <option value="Animal Welfare">Animal Welfare</option>
          </optgroup>
          <optgroup label="Environmental">
            <option value="Plume">Plume</option>
            <option value="Radiation Pollution">Radiation Pollution</option><i class="fas fa-radiation-alt"></i>
            <option value="Hazardous Chemical Pollution">Hazardous Chemical Pollution</option>
            <option value="Oil Pollution">Oil Pollution</option>
            <option value="Sewage / Slurry">Sewage / Slurry</option>
          </optgroup>
        </select>
      </div>
      <div class="form-group mt-3 mb-3">
        <input v-model="reportedVia" class="form-control" placeholder="Reported Via" type="text" required>
      </div>
      <div class="form-group mb-3">
        <input v-model="reference" class="form-control" placeholder="Reference (Optional)" type="text">
      </div>
      <div class="form-group mb-3">
        <input v-model="address" class="form-control" placeholder="Address" type="text">
      </div>
      <span id="LocationNotChosen" class="text-danger d-none">Please select the location of the incident.</span>
      <div id="Map" class="map-container">
        <MglMap :accessToken="accessToken" :mapStyle="mapStyle" @click="onClickMap" :center="[-4.003661, 56.584255]">
          <MglGeocoderControl :accessToken="accessToken" :input="searchResult" @result="handleResult" :draggable="true" />
          <MglMarker v-if="markerSet" :coordinates="location" :draggable="true" color="blue" ref="marker" />
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

import router from '@/router/index'
import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'NewIncidentModal',
  mixins: [ModalMixin],
  components: {
    MglMap,
    MglMarker,
    MglGeocoderControl
  },
  props: {
    deploymentName: String,
    deploymentId: Number
  },
  data () {
    return {
      name: '',
      description: '',
      type: null,
      reportedVia: '',
      reference: '',
      address: '',
      markerSet: false,
      location: [0, 0],
      accessToken: Vue.prototype.$mapBoxApiKey,
      mapStyle: 'mapbox://styles/mapbox/streets-v11',
      searchResult: ''
    }
  },
  methods: {
    handleSubmit (e) {
      if (!this.name.length || !this.description.length || !this.type) {
        return
      }
      Vue.prototype.$api
        .post(`deployments/${this.deploymentId}`, { name: this.name, description: this.description, type: this.type, reportedVia: this.reportedVia, reference: this.reference, address: this.address, longitude: this.location[0], latitude: this.location[1] })
        .then(r => r.data)
        .then(data => {
          this.$emit('close')
          document.body.classList.remove('modal-open')
          this.name = ''
          this.description = ''
          this.type = ''
          this.reportedVia = ''
          this.reference = ''
          this.address = ''
          this.location = []
          e.target.reset()
          router.push({ name: 'incident', params: { deploymentName: this.deploymentName.replace(/ /g, '-'), deploymentId: this.deploymentId, incidentName: data.name.replace(/ /g, '-'), incidentId: data.id } })
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
