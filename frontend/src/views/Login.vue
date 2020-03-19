<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-xl-5 col-lg-6 col-md-4">
        <div class="card o-hidden border-0 shadow-lg my-5">
          <div class="card-body p-0">
            <div v-if="forgotPassword" class="p-5">
              <div class="text-center">
                <h1 class="h4 text-gray-900 mb-4">Forgotten Password</h1>
              </div>
              <form class="user" @submit.prevent="requestPasswordReset">
                <div :class="['alert', 'text-center', passwordResetSuccess ? 'alert-success' : 'alert-danger']" v-if="passwordResetSuccess || passwordResetError">{{ passwordResetSuccess ? 'Sent email with password reset' : 'Incorrect email provided' }}</div>
                <div class="form-group">
                  <input v-model="email" type="email" class="form-control form-control-user" name="email" placeholder="Enter Email" aria-label="Email" required autofocus>
                </div>
                <button type="submit" class="btn btn-primary btn-user btn-block mt-4">Request Password Reset</button>
              </form>
              <hr>
              <div class="text-center">
                <a class="small" @click="forgotPassword = false">Login?</a>
              </div>
            </div>
            <div v-else class="p-5">
              <div class="text-center">
                <h1 class="h4 text-gray-900 mb-4">Log in to DGVOST</h1>
              </div>
              <form class="user" @submit.prevent="login">
                <div class="alert alert-danger text-center" v-if="loginError">Incorrect login details provided</div>
                <div class="form-group">
                  <input v-model="email" type="email" class="form-control form-control-user" name="email" placeholder="Enter Email" aria-label="Email" required autofocus>
                </div>
                <div class="form-group">
                  <input v-model="password" type="password" class="form-control form-control-user" name="password" placeholder="Enter Password" aria-label="Password" required>
                </div>
                <div class="form-group">
                    <input v-model="rememberMe" class="mx-1 checkbox-primary" type="checkbox" id="rememberMe">
                    <label class="text-s" for="rememberMe">Remember Me</label>
                </div>
                <button type="submit" class="btn btn-primary btn-user btn-block">Sign in</button>
              </form>
              <hr>
              <div class="text-center">
                <a class="small" @click="forgotPassword = true">Forgot Password?</a>
              </div>
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
  name: 'login',
  data () {
    return {
      email: '',
      password: '',
      rememberMe: false,
      forgotPassword: false,
      passwordResetSuccess: false,
      passwordResetError: false,
      loginError: false
    }
  },
  methods: {
    requestPasswordReset () {
      Vue.prototype.$api
        .post('users/request-password-reset', { email: this.email })
        .then(() => {
          this.passwordResetSuccess = true
        })
        .catch(() => {
          this.passwordResetError = true
        })
    },
    login () {
      this.$store.dispatch('user/login', [this.email, this.password])
        .then(() => {
          if (this.rememberMe) {
            localStorage.rememberMeEmail = this.email
          } else {
            localStorage.removeItem('rememberMeEmail')
          }
          this.$router.push(this.$route.query.redirect || { name: 'deployments' })
        })
        .catch(() => this.loginFailed())
    },
    loginFailed () {
      this.password = ''
      this.loginError = true
    }
  },
  beforeCreate () {
    if (this.$store.getters['user/loggedIn']) {
      this.$router.push({ name: 'deployments' })
    }
  },
  created: function () {
    document.body.classList.add('bg-gradient-primary')
    if (localStorage.rememberMeEmail) {
      this.email = localStorage.rememberMeEmail
      this.rememberMe = true
    }
  },
  beforeDestroy () {
    document.body.classList.remove('bg-gradient-primary')
  }
}
</script>
