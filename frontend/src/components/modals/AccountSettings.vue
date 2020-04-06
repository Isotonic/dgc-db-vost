<template>
  <modal :title="'Account Settings'" :bigger="true" :bgLight="true" @close="close">
    <div>
      <img alt="Avatar" :src="$developmentMode ? `http://localhost:5000${user.avatarUrl}?${cacheFix}` : user.avatarUrl + cacheFix" class="rounded-circle avatar card-img avatar-lg">
      <span class="h4 font-weight-bold ml-4">{{ user.firstname }} {{ user.surname }}{{ user.group ? ' - ' + user.group.name : '' }}</span>
    </div>
    <div class="mt-3">
    <div class="upload-btn-wrapper">
      <input type="file" class="hover" @change="uploadImage">
      <button class="btn btn-primary btn-sm mr-3">Upload avatar</button>
    </div>
      <button class="btn btn-danger btn-sm p-absolute" @click="deleteImage">Remove avatar</button>
    </div>
    <hr />
    <form class="form-group" @submit.prevent="submitDetails">
      <label for="firstname" class="text-primary font-weight-bold">Firstname:</label>
      <input v-model="firstname" id="firstname" class="form-control form-control-sm" placeholder="Enter your firstname..." type="text" required>
      <label for="surname" class="text-primary font-weight-bold mt-2">Surname:</label>
      <input v-model="surname" id="surname" class="form-control form-control-sm" placeholder="Enter your surname..." type="text" required>
      <label for="email" class="text-primary font-weight-bold mt-2">Email:</label>
      <input v-model="email" id="email" class="form-control form-control-sm" placeholder="Enter your email..." type="email" required>
      <label v-if="changePassword" for="newPassword" class="text-primary font-weight-bold mt-2">New password:</label>
      <input v-if="changePassword" v-model="newPassword" id="newPassword" class="form-control form-control-sm" placeholder="Enter your new password..." type="password" required>
      <label v-if="changePassword" for="newPasswordRepeated" class="text-primary font-weight-bold mt-2">Re-enter New password:</label>
      <input v-if="changePassword" v-model="newPasswordRepeated" id="newPasswordRepeated" class="form-control form-control-sm" placeholder="Re-enter your new password..." type="password" @blur="stoppedTyping = true" required>
      <div v-if="changePassword" class="mt-2">
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
      <label v-if="changePassword || firstname !== user.firstname || surname !== user.surname || email !== user.email || email !== user.email" for="currentPassword" class="text-primary font-weight-bold mt-2">Current password:</label>
      <input v-if="changePassword || firstname !== user.firstname || surname !== user.surname || email !== user.email || email !== user.email" v-model="currentPassword" id="currentPassword" class="form-control form-control-sm" placeholder="Enter your current password..." type="password" required>
      <div class="mt-3"><span v-if="!changePassword" class="font-weight-bold text-primary text-sm hover" @click="changePassword = true">Change Password?</span></div>
      <button v-if="currentPassword.length" type="submit" class="btn btn-primary btn-user btn-block mt-4">Submit</button>
    </form>
  </modal>
</template>

<script>
import Vue from 'vue'
import { mapGetters, mapActions } from 'vuex'

import { ModalMixin } from '@/utils/mixins'

export default {
  name: 'AccountSettingsModal',
  mixins: [ModalMixin],
  data () {
    return {
      firstname: null,
      surname: null,
      email: null,
      newPassword: '',
      newPasswordRepeated: '',
      currentPassword: '',
      changePassword: false,
      stoppedTyping: false,
      error: false,
      cacheFix: 0,
      rules: [
        { message: 'Contain a lowercase letter.', regex: /[a-z]+/ },
        { message: 'Contain an uppercase letter.', regex: /[A-Z]+/ },
        { message: 'Contain a number.', regex: /[0-9]+/ },
        { message: 'Be 8 characters minimum.', regex: /.{8,}/ }
      ]
    }
  },
  methods: {
    uploadImage (event) {
      const selectedFile = event.target.files[0]
      const formData = new FormData()
      formData.append('file', selectedFile, selectedFile.name)
      this.ApiPost('/users/avatar', formData)
        .then(() => {
          this.cacheFix += 1
          Vue.noty.success('Successfully changed avatar')
        })
        .catch((error) => {
          Vue.noty.error(error.response.data.message)
        })
    },
    deleteImage () {
      this.ApiDelete('/users/avatar')
        .then(() => {
          this.cacheFix += 1
          Vue.noty.success('Successfully deleted avatar')
        })
        .catch((error) => {
          Vue.noty.error(error.response.data.message)
        })
    },
    submitDetails () {
      if (this.firstname !== '' && this.surname !== '' && this.email !== '' && this.passwordValidation) {
        let data = { firstname: this.firstname, surname: this.surname, email: this.email, currentPassword: this.currentPassword }
        if (this.newPassword !== '') {
          data.newPassword = this.newPassword
        }
        this.$api
          .put('users/me', data)
          .then(r => r.data)
          .then(data => {
            this.updateDetails([data.firstname, data.surname, data.email])
            if (data.accessToken) {
              this.updateTokens([data.access_token, data.refresh_token])
            }
            this.$emit('close')
          })
          .catch((error) => {
            Vue.noty.error(error.response.data.message)
          })
      }
    },
    checkValid (regex) {
      if (regex.test(this.newPassword)) {
        return true
      } else {
        return false
      }
    },
    ...mapActions('user', {
      updateDetails: 'updateDetails'
    })
  },
  computed: {
    passwordsNotSame () {
      if (this.newPassword) {
        return (this.newPassword !== this.newPasswordRepeated)
      } else {
        return false
      }
    },
    passwordsEntered () {
      return (this.newPassword !== '' && this.newPasswordRepeated !== '')
    },
    passwordValidation () {
      if (this.newPassword === '' && this.newPasswordRepeated === '') {
        return true
      }
      for (let condition of this.rules) {
        if (!condition.regex.test(this.newPassword)) {
          return false
        }
      }
      return true
    },
    ...mapGetters('user', {
      user: 'getUser'
    })
  },
  created () {
    this.firstname = this.user.firstname
    this.surname = this.user.surname
    this.email = this.user.email
  }
}
</script>
