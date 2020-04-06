<template>
  <modal :title="'Edit Details'" @close="close">
    <form @submit.prevent="handleSubmit" aria-label="Create new user">
      <div class="form-group mb-4">
        <input v-model="name" class="form-control" placeholder="Name" type="text" required>
      </div>
      <div class="form-group mb-4">
        <textarea-autosize v-model="description" class="form-control" placeholder="Description" type="text" required />
      </div>
      <div class="form-group mb-4">
        <select v-model="type" class="custom-select custom-select-sm text-primary font-weight-bold full-length">
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
      <div class="form-group mb-4">
        <input v-model="reportedVia" class="form-control" placeholder="Reported Via" type="text">
      </div>
      <multiselect v-model="linkedIncidents" class="mb-4" :options="filteredLinkedIncidents" :multiple="true" placeholder="Type to search incidents to link" track-by="id" :custom-label="formatSelect" :closeOnSelect="false" openDirection="bottom" :limit="0" :limitText="count => count > 1 ? `${count} incidents are linked.` : `${count} incident is linked.`" :blockKeys="['Delete']" selectedLabel="Linked">
        <template v-if="didLinkedChange" slot="clear">
          <div class="multiselect__clear" v-tooltip.right="'Reset changes'" @mousedown.prevent.stop="setLinkedSelecter"></div>
        </template>
        <span slot="noResult">Oops! No incidents found.</span>
      </multiselect>
      <div class="form-group mb-4">
        <input v-model="reference" class="form-control" placeholder="Reference Number (If Provided)" type="text">
      </div>
      <div class="text-center">
        <button type="submit" class="btn btn-primary mt-1">Save</button>
      </div>
    </form>
  </modal>
</template>

<script>
import Multiselect from 'vue-multiselect'
import { mapGetters } from 'vuex'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'IncidentDetailsModal',
  mixins: [ModalMixin],
  components: {
    Multiselect
  },
  props: {
    title: String,
    visible: Boolean,
    incident: Object
  },
  data () {
    return {
      name: this.incident.name,
      description: this.incident.description,
      type: this.incident.type,
      reportedVia: this.incident.reportedVia,
      linkedIncidents: this.incident.linkedIncidents,
      reference: this.incident.reference
    }
  },
  methods: {
    handleSubmit (e) {
      if (!this.name.length) {
        return
      } else if (this.hasntChanged) {
        this.$emit('close')
      }
      let incidentData = { name: this.name, type: this.type }

      if (this.description.length) {
        incidentData.description = this.description
      }

      if (this.reportedVia && this.reportedVia.length) {
        incidentData.reportedVia = this.reportedVia
      }

      if (this.linkedIncidents.length) {
        incidentData.linkedIncidents = this.linkedIncidents.map(incident => incident.id)
      }

      if (this.reference && this.reference.length) {
        incidentData.reference = this.reference
      }

      this.ApiPut(`incidents/${this.incident.id}`, incidentData)
        .then(() => {
          this.$emit('close')
        })
    },
    formatSelect: function ({ name, id }) {
      return `${name} - ${id}`
    },
    setLinkedSelecter () {
      this.linkedIncidents = this.incident.linkedIncidents
    }
  },
  computed: {
    filteredLinkedIncidents: function () {
      return this.incidents.filter(incident => incident.id !== this.incident.id)
    },
    hasntChanged: function () {
      return this.name === this.incident.name && this.description === this.incident.description && this.reportedVia === this.incident.reportedVia && this.reference === this.incident.reference && !this.didLinkedChange
    },
    didLinkedChange: function () {
      return this.linkedIncidents.length !== this.incident.linkedIncidents.length ||
      !this.linkedIncidents.every(e => this.incident.linkedIncidents.includes(e))
    },
    ...mapGetters('incidents', {
      incidents: 'getIncidents'
    })
  }
}
</script>
