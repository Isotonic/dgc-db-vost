import Vue from 'vue'
import Modal from '@/components/utils/Modal'

export const ApiMixin = {
  methods: {
    ApiPost: function (url, data) {
      return new Promise((resolve, reject) => {
        Vue.prototype.$api
          .post(url, data)
          .then(r => r.data)
          .then(data => {
            // Vue.noty.success(data)
            resolve()
          })
          .catch(error => {
            console.log(error.response.data.message)
            Vue.noty.error(error.response.data.message)
            reject(error)
          })
      })
    },
    ApiPut: function (url, data) {
      return new Promise((resolve, reject) => {
        Vue.prototype.$api
          .put(url, data)
          .then(r => r.data)
          .then(data => {
            // Vue.noty.success(data)
            resolve()
          })
          .catch(error => {
            console.log(error.response.data.message)
            Vue.noty.error(error.response.data.message)
            reject(error)
          })
      })
    },
    ApiDelete: function (url) {
      return new Promise((resolve, reject) => {
        Vue.prototype.$api
          .delete(url)
          .then(r => r.data)
          .then(data => {
            // Vue.noty.success(data)
            resolve()
          })
          .catch(error => {
            console.log(error.response.data.message)
            Vue.noty.error(error.response.data.message)
            reject(error)
          })
      })
    }
  }
}

export const ModalMixin = {
  components: {
    Modal
  },
  props: {
    visible: Boolean
  },
  methods: {
    close () {
      document.body.classList.remove('modal-open')
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
  },
  beforeDestroy () {
    if (document.body.classList.contains('modal-open')) {
      document.body.classList.remove('modal-open')
    }
  }
}
