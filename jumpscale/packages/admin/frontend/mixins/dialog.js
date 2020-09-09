dialog = {
  props: { value: Boolean },
  data () {
    return {
      form: {},
      error: null,
      info: null,
      warning: null,
      loading: false
    }
  },
  computed: {
    dialog: {
      get () {
        return this.value
      },
      set (value) {
        this.$emit('input', value)
      }
    },
  },
  methods: {
    done (message) {
      this.close()
      this.$emit("done")
      this.$root.$emit('popup', message, "success")
    },
    reset () {
      this.form = {}
    },
    close () {
      this.error = null
      this.info = null
      this.warning = null
      this.dialog = false
      this.reset()
    }
  }
}
