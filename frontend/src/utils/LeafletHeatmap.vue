<!--
Copyright (c) 2020 by Jurian (https://github.com/jurb/vue2-leaflet-heatmap)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 -->

<template>
  <div style="display: none;">
    <slot v-if="ready"></slot>
  </div>
</template>

<script>
import { findRealParent, propsBinder } from 'vue2-leaflet'
import { heatLayer, DomEvent } from 'leaflet'
import 'leaflet.heat'

const props = {
  latLng: {
    type: Array,
    default: () => [],
    custom: false
  },
  minOpacity: {
    type: Number,
    custom: true,
    default: 0.05
  },
  maxZoom: {
    type: Number,
    custom: true,
    default: 18
  },
  radius: {
    type: Number,
    custom: true,
    default: 25
  },
  blur: {
    type: Number,
    custom: true,
    default: 15
  },
  max: {
    type: Number,
    custom: true,
    default: 1.0
  },
  visible: {
    type: Boolean,
    custom: true,
    default: true
  }
}
export default {
  name: 'LHeatmap',
  props,
  data () {
    return {
      ready: false
    }
  },
  mounted () {
    const options = {}
    if (this.minOpacity) {
      options.minOpacity = this.minOpacity
    }
    if (this.maxZoom) {
      options.maxZoom = this.maxZoom
    }
    if (this.radius) {
      options.radius = this.radius
    }
    if (this.blur) {
      options.blur = this.blur
    }
    if (this.max) {
      options.max = this.max
    }
    this.mapObject = heatLayer(this.latLng, options)
    DomEvent.on(this.mapObject, this.$listeners)
    propsBinder(this, this.mapObject, props)
    this.$emit('ready')
    this.ready = true
    this.parentContainer = findRealParent(this.$parent)
    this.parentContainer.addLayer(this, !this.visible)
  },
  beforeDestroy () {
    this.parentContainer.removeLayer(this)
  },
  methods: {
    setMinOpacity (newVal) {
      this.mapObject.setOptions({ minOpacity: newVal })
    },
    setMaxZoom (newVal) {
      this.mapObject.setOptions({ maxZoom: newVal })
    },
    setRadius (newVal) {
      this.mapObject.setOptions({ radius: newVal })
    },
    setBlur (newVal) {
      this.mapObject.setOptions({ blur: newVal })
    },
    setMax (newVal) {
      this.mapObject.setOptions({ max: newVal })
    },
    setVisible (newVal, oldVal) {
      if (newVal === oldVal) return
      if (newVal) {
        this.parentContainer.addLayer(this)
      } else {
        this.parentContainer.removeLayer(this)
      }
    },
    addLatLng (value) {
      this.mapObject.addLatLng(value)
    }
  }
}
</script>

<style>
</style>
