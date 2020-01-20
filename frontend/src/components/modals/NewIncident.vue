<template>
  <Modal :title="'New Incident'" @close="close">
    <form aria-label="Add a new incident">
      <div class="form-group mb-3">
        <input class="form-control was-validated" name="name" placeholder="Incident Name" type="text" required>
      </div>
      <textarea class="form-control" rows="3" name="description" placeholder="Description"></textarea>
      <div class="form-group my-3">
        <select id="newIncidentCategory" name="category" style="width: 100%">
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
        <input class="form-control" name="reported_via" placeholder="Reported Via" type="text" required>
      </div>
      <div class="form-group mb-3">
        <input class="form-control" name="reference" placeholder="Reference (Optional)" type="text">
      </div>
      <span id="LocationNotChosen" class="text-danger d-none">Please select the location of the incident.</span>
      <div class="text-center">
        <button type="submit" class="btn btn-primary my-4">Submit</button>
      </div>
    </form>
  </Modal>
</template>

<script>
import Modal from '@/components/utils/Modal.vue'

export default {
  name: 'NewIncidentModal',
  components: {
    Modal
  },
  props: {
    title: String,
    visible: Boolean
  },
  methods: {
    close () {
      this.$emit('close')
    }
  },
  watch: {
    visible: function () {
      if (this.visible) {
        document.body.classList.add('modal-open')
        return
      }
      document.body.classList.remove('modal-open')
    }
  },
  created: function () {
    if (this.visible) {
      document.body.classList.add('modal-open')
    }
  }
}
</script>
