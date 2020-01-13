<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-xl-5 col-lg-6 col-md-4">
        <div class="card o-hidden border-0 shadow-lg my-5">
          <div class="card-body p-0">
            <div class="p-5">
              <div class="text-center">
                <h1 class="h4 text-gray-900 mb-4">Log in to DGVOST</h1>
              </div>
              <form class="user" @submit.prevent="login">
                <div class="alert alert-danger text-center" v-if="error">Incorrect login details provided</div>
                <div class="form-group">
                  <input v-model="email" type="email" class="form-control form-control-user" name="email" placeholder="Enter Email" required autofocus>
                </div>
                <div class="form-group">
                  <input v-model="password" type="password" class="form-control form-control-user" name="password" placeholder="Enter Password" required>
                </div>
                <div class="form-group">
                  <div class="custom-control custom-checkbox small">
                    <input type="checkbox" class="custom-control-input" name="remember_me" id="customCheckLogin">
                    <label class="custom-control-label" for="customCheckLogin">Remember Me</label>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary btn-user btn-block">Sign in</button>
              </form>
              <hr>
              <div class="text-center">
                <a class="small" href="forgot-password.html">Forgot Password?</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'login',
  data () {
    return {
      email: '',
      password: '',
      error: false
    }
  },
  methods: {
    login () {
      this.$store.dispatch('user/login', [this.email, this.password])
        .then(() => this.$router.push(this.$route.query.redirect || { name: 'deployments' }))
        .catch(() => this.loginFailed())
    },
    loginFailed () {
      this.email = ''
      this.password = ''
      this.error = true
    }
  },
  beforeCreate () {
    if (this.$store.getters['user/loggedIn']) {
      this.$router.push({ name: 'deployments' })
    }
  }
}
</script>
