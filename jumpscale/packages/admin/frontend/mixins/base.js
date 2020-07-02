base = {
  methods: {
    alert (message, status) {
      this.$root.$emit('popup', message, status)
    }
  }
}