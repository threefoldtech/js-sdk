<template>
  <div>
    <Message :payload="payload"></Message>
    <div id="map"></div><br>
    <v-row>
      <v-col cols="12" md="6">
        <v-text-field v-model="lat" type="number" label="Latitude" :rules="rules" validate-on-blur outlined></v-text-field>
      </v-col>
      <v-col cols="12" md="6">
        <v-text-field v-model="lng" type="number" label="Longitude" :rules="rules" validate-on-blur outlined></v-text-field>
      </v-col>
    </v-row>
  </div>
</template>

<script>

mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw'

module.exports = {
  mixins: [field],
  props: {payload: Object},
  data () {
    return {
      map: null,
      marker: null,
      lat: null,
      lng: null,
      zoom: 1
    }
  },
  watch: {
    lat () {
      this.marker.setLngLat([this.lng, this.lat])
    },
    lng () {
      this.marker.setLngLat([this.lng, this.lat])
    }
  },
  methods: {
    init () {
      this.map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/streets-v9',
        zoom: this.zoom
      })
      this.marker = new mapboxgl.Marker({draggable: true})
      this.marker.setLngLat([this.lng, this.lat]).addTo(this.map)
      this.marker.on('dragend', this.dragend);
    },
    fly () {
      this.map.flyTo({center: [this.lng, this.lat], essential: true})
    },
    dragend () {
      var coordinates = this.marker.getLngLat()
      this.zoom = 5
      this.lat = coordinates.lat
      this.lng = coordinates.lng
      this.val = [this.lng, this.lat]
      this.fly()
    }
  },
  mounted () {
    this.$nextTick(() => {
      if (this.val && this.val.length > 0) {
        this.lng = this.val[0]
        this.lat = this.val[1]
        this.zoom = 5  
      } else {
        this.val = []
        this.zoom = 1
      }
      this.init()
      this.fly()
    })
  }
}
</script>

<style scoped>
  #map {
    width: 100% !important;
    height: 500px !important;
    border-radius: 10px;
  }
</style>
