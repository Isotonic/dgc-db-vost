<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-xl-5 col-lg-6 col-md-4">
        <div class="card o-hidden border-0 shadow-lg my-5">
          <div class="card-body p-0">
            <div class="p-5">
              <div class="text-center">
                <h1 class="h4 text-gray-900 mb-4">Complete DGVOST Registration</h1>
              </div>
              <form class="user" @submit.prevent="register">
                <div class="alert alert-danger text-center" v-if="error">Registration link does not exist or was revoked. Please ask a supervisor to send a new one.</div>
                <div v-else>
                  <div class="form-group">
                    <input v-model="firstname" type="text" class="form-control form-control-user" placeholder="Enter Firstname" aria-label="Firstname" required autofocus>
                  </div>
                  <div class="form-group">
                    <input v-model="surname" type="text" class="form-control form-control-user" placeholder="Enter Surname" aria-label="Surname" required autofocus>
                  </div>
                  <div class="form-group">
                    <input v-model="password" type="password" class="form-control form-control-user" placeholder="Enter Password" aria-label="Password" required>
                  </div>
                  <div class="form-group">
                    <input v-model="checkPassword" type="password" class="form-control form-control-user" placeholder="Re-enter Password" aria-label="Password re-entered" @blur="stoppedTyping = true" required>
                  </div>
                  <div>
                    <h6 :class="['font-weight-bold', 'text-primary']">Password must:</h6>
                      <div v-for="rule in rules" :key="rule.message">
                        <input class="mr-2" type="checkbox" :checked="checkValid(rule.regex)" disabled>
                        <span class="ml-4">{{ rule.message }}<br></span>
                      </div>
                      <div v-if="passwordsNotSame && stoppedTyping">
                        <input class="mr-2 checkbox-error" type="checkbox" :checked="true" disabled>
                        <span class="ml-4">Match<br></span>
                      </div>
                  </div>
                  <button type="submit" class="btn btn-primary btn-user btn-block mt-4">Submit</button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'registration',
  props: {
    link: String
  },
  data () {
    return {
      email: '',
      firstname: '',
      surname: '',
      password: '',
      checkPassword: '',
      stoppedTyping: false,
      successful: false,
      error: false,
      rules: [
        { message: 'Contain a lowercase letter.', regex: /[a-z]+/ },
        { message: 'Contain an uppercase letter.', regex: /[A-Z]+/ },
        { message: 'Contain a number.', regex: /[0-9]+/ },
        { message: 'Be 8 characters minimum.', regex: /.{8,}/ }
      ]
    }
  },
  methods: {
    register () {
      if (this.firstname !== '' && this.surname !== '' && this.passwordValidation && !this.passwordsNotSame) {
        Vue.prototype.$http
          .put(`users/complete-registration/${this.link}`, { firstname: this.firstname, surname: this.surname, password: this.password })
          .then(() => {
            this.successful = true
            this.$router.push({ name: 'login' })
            Vue.noty.success('Successfully registered, please login.')
          })
          .catch((error) => {
            Vue.noty.error(error.response.data.message)
          })
      }
    },
    checkValid (regex) {
      if (regex.test(this.password)) {
        return true
      } else {
        return false
      }
    }
  },
  computed: {
    passwordsNotSame () {
      if (this.passwordsEntered) {
        return (this.password !== this.checkPassword)
      } else {
        return false
      }
    },
    passwordsEntered () {
      return (this.password !== '' && this.checkPassword !== '')
    },
    passwordValidation () {
      for (let condition of this.rules) {
        if (!condition.regex.test(this.password)) {
          return false
        }
      }
      return true
    }
  },
  beforeCreate () {
    if (this.$store.getters['user/loggedIn']) {
      this.$router.push({ name: 'deployments' })
      Vue.noty.error('You are currently logged in.')
    }
  },
  created: function () {
    document.body.classList.add('bg-gradient-primary')
    Vue.prototype.$http
      .get(`users/verify-registration-link/${this.link}`)
      .then(r => r.data)
      .then((data) => {
        this.email = data.email
      })
      .catch(() => {
        this.error = true
      })
  },
  beforeDestroy () {
    if (!this.successful) {
      document.body.classList.remove('bg-gradient-primary')
    }
  }
}
</script>
