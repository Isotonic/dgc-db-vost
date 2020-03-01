<template>
  <div id="wrapper">
    <div id="content-wrapper" class="d-flex flex-column">
      <topbar :nosidebar="true" :goToDeployments="true" />
      <div class="container-fluid">
        <div class="d-sm-flex align-items-center justify-content-between mb-4">
          <h1 class="font-weight-bold mb-0">Admin Settings</h1>
          <button @click="openNewModal" class="btn btn-icon-split btn-success mb-1 mt-2">
            <span class="btn-icon">
              <i class="fas fa-plus"></i>
            </span>
            <span class="text">{{ showingUsers ? 'New User' : 'New Group'}}</span>
          </button>
        </div>
        <new-user-modal v-if="isNewUserModalVisible" v-show="isNewUserModalVisible" :visible="isNewUserModalVisible" :groups="groups" @close="isNewUserModalVisible = false" />
        <group-modal v-if="isNewGroupModalVisible" v-show="isNewGroupModalVisible" :visible="isNewGroupModalVisible" @close="isNewGroupModalVisible = false" />
        <div class="row">
          <div class="col-xl-12 col-lg-10">
            <div class="card shadow mb-4">
              <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                <h6 class="m-0 font-weight-bold text-primary">Incidents</h6>
                <select v-model="showingUsers" class="custom-select custom-select-sm text-primary font-weight-bold">
                  <option :value="true">Users</option>
                  <option :value="false">Groups</option>
                </select>
              </div>
              <div class="card-body">
                <div class="table-responsive">
                  <v-client-table v-if="showingUsers" :data="users" :columns="usersColumns" :options="usersOptions">
                    <div slot="group" slot-scope="{row}">
                      <span v-if="user.id !== row.id">
                        <select :value="row.group ? row.group.id : null" @change="changeUserGroup(row.id, $event.target.value)" class="custom-select custom-select-sm text-primary font-weight-bold">
                          <option :value="null">None</option>
                          <option disabled>──────────</option>
                          <option v-for="group in orderBy(groups, 'id')" :key="group.id" :value="group.id">{{ group.name }}</option>
                        </select>
                      </span>
                      <span v-else class="text-primary font-weight-bold ml-2">{{ row.group ? row.group.name : 'None' }}</span>
                    </div>
                    <div slot="status" slot-scope="{row}">
                      <span v-if="row.status == 0">
                        <span>Sent email</span>
                        <i class="fas fa-redo-alt ml-3" @click="resendEmail(row)" v-tooltip="'Resend email'"></i>
                        <i class="fas fa-times ml-2" @click="confirmRevokeUser(row)" v-tooltip="'Revoke'"></i>
                      </span>
                      <span v-else-if="user.id !== row.id">
                        <select :value="row.status" @change="changeUserStatus(row.id, $event.target.value)" class="custom-select custom-select-sm text-primary font-weight-bold">
                          <option :value="1">Active</option>
                          <option :value="-1">Disabled</option>
                        </select>
                      </span>
                      <span v-else class="text-primary font-weight-bold ml-2">Active</span>
                    </div>
                  </v-client-table>
                  <question-modal v-if="isRevokeUserModalVisible" v-show="isRevokeUserModalVisible" :visible="isRevokeUserModalVisible" :title="'Revoke Email'" @btnAction="revokeUser" @close="isRevokeUserModalVisible = false">
                    <template v-slot:question>
                      <div class="text-center">
                        <span class="font-weight-bold">Are you sure you wish to revoke the email sent to <code>{{ revokeUserObj.email }}</code>?</span>
                      </div>
                    </template>
                  </question-modal>
                  <v-client-table v-if="!showingUsers" :data="groups" :columns="groupsColumns" :options="groupsOptions">
                    <div slot="members" slot-scope="{row}">
                      <span>
                        {{ membersInGroup(row) }}
                      </span>
                    </div>
                    <div slot="settings" slot-scope="{row}">
                      <i class="fas fa-cogs hover text-primary pl-2" @click="editGroup(row)"></i>
                      <i class="fas fa-trash-alt hover text-danger pl-3" @click="confirmDeleteGroup(row)"></i>
                    </div>
                  </v-client-table>
                  <group-modal v-if="isEditGroupModalVisible" v-show="isEditGroupModalVisible" :visible="isEditGroupModalVisible" :edit="true" :group="editGroupObj" @close="isEditGroupModalVisible = false" />
                  <question-modal v-if="isDeleteGroupModalVisible" v-show="isDeleteGroupModalVisible" :visible="isDeleteGroupModalVisible" :title="'Delete Group'" @btnAction="deleteGroup" @close="isDeleteGroupModalVisible = false">
                    <template v-slot:question>
                      <div class="text-center">
                        <span class="font-weight-bold">Are you sure you wish to delete <code>{{ deleteGroupObj.name }}</code>?</span>
                      </div>
                    </template>
                  </question-modal>
                </div>
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
import Vue2Filters from 'vue2-filters'
import { mapActions, mapGetters } from 'vuex'

import Topbar from '@/components/Topbar'
import QuestionModal from '@/components/modals/Question'
import NewUserModal from '@/components/modals/NewUser'
import GroupModal from '@/components/modals/Group'

function capitalLetters (str) {
  str = str.split(' ')
  for (let i = 0, x = str.length; i < x; i++) {
    str[i] = str[i][0].toUpperCase() + str[i].substr(1)
  }
  return str.join(' ')
}

function makeString (arr) {
  if (arr.length === 1) return arr[0]
  const firsts = arr.slice(0, arr.length - 1)
  const last = arr[arr.length - 1]
  return firsts.join(', ') + ' and ' + last
}

export default {
  name: 'Admin',
  mixins: [Vue2Filters.mixin],
  components: {
    Topbar,
    QuestionModal,
    NewUserModal,
    GroupModal
  },
  data () {
    return {
      showingUsers: false,
      users: [],
      groups: [],
      deleteGroupObj: null,
      editGroupObj: null,
      isRevokeUserModalVisible: false,
      isDeleteGroupModalVisible: false,
      isEditGroupModalVisible: false,
      isNewUserModalVisible: false,
      isNewGroupModalVisible: false,
      usersColumns: ['name', 'email', 'group', 'status', 'createdAt'],
      usersOptions: {
        headings: {
          name: 'Name',
          email: 'Email',
          group: 'Group',
          status: 'Status',
          createdAt: 'Created At'
        },
        templates: {
          name: function (h, row, index) {
            return row.firstname && row.surname ? `${row.firstname} ${row.surname}` : 'N/A'
          },
          createdAt: function (h, row, index) {
            return this.$moment.unix(row.createdAt).fromNow()
          }
        },
        customSorting: {
          name: function (ascending) {
            return function (a, b) {
              let lastA = `${a.firstname} ${a.surname}`
              let lastB = `${b.firstname} ${b.surname}`

              if (lastA === lastB) {
                lastA = a.createdAt
                lastB = b.createdAt
              }
              if (ascending) {
                return lastA >= lastB ? 1 : -1
              }
              return lastA <= lastB ? 1 : -1
            }
          }
        },
        filterAlgorithm: {
          name (row, query) {
            return row.firstname && row.surname ? (`${row.firstname} ${row.surname}`).toLowerCase().includes(query) : 'n/a'.includes(query)
          }
        },
        orderBy: {
          column: 'name',
          ascending: true
        },
        summary: 'Table of users',
        resizeableColumns: true,
        sortIcon: { base: 'float-right fas', up: 'fa-sort-up', down: 'fa-sort-down', is: 'fa-sort' },
        highlightMatches: true
      },
      groupsColumns: ['name', 'permissions', 'members', 'settings'],
      groupsOptions: {
        headings: {
          name: 'Name',
          permissions: 'Permissions',
          members: 'Members',
          settings: 'Settings'
        },
        templates: {
          permissions: function (h, row, index) {
            if (!row.permissions.length) {
              return 'None'
            }
            return makeString(row.permissions.map(permission => capitalLetters(permission.replace(/_/g, ' '))))
          }
        },
        filterAlgorithm: {
          permissions (row, query) {
            if (!row.permissions.length) {
              return 'none'.includes(query)
            }
            return makeString(row.permissions.map(permission => capitalLetters(permission.replace(/_/g, ' ')))).toLowerCase().includes(query)
          }
        },
        customSorting: {
          permissions: function (ascending) {
            return function (a, b) {
              let lastA = a.permissions.length
              let lastB = b.permissions.length

              if (lastA === lastB) {
                lastA = a.createdAt
                lastB = b.createdAt
              }
              if (ascending) {
                return lastA >= lastB ? 1 : -1
              }
              return lastA <= lastB ? 1 : -1
            }
          }
        },
        orderBy: {
          column: 'name',
          ascending: true
        },
        summary: 'Table of groups',
        resizeableColumns: true,
        sortable: ['name', 'permissions', 'members'],
        sortIcon: { base: 'float-right fas', up: 'fa-sort-up', down: 'fa-sort-down', is: 'fa-sort' },
        highlightMatches: true
      }
    }
  },
  sockets: {
    new_user: function (data) {
      console.log('Recieved new user event')
      this.users.push(data.user)
    },
    new_group: function (data) {
      console.log('Recieved new group event')
      this.groups.push(data.group)
    },
    change_user_group: function (data) {
      console.log('Recieved change user group event')
      const user = this.users.find(user => user.id === data.id)
      if (user) {
        user.group = data.group
      }
    },
    change_user_status: function (data) {
      console.log('Recieved change user status event')
      const user = this.users.find(user => user.id === data.id)
      if (user) {
        user.status = data.status
      }
    },
    edit_group: function (data) {
      console.log('Recieved group edit event')
      const group = this.groups.find(group => group.id === data.id)
      if (group) {
        group.name = data.name
        group.permissions = data.permissions
      }
    },
    delete_user: function (data) {
      console.log('Recieved delete user event')
      this.users = this.users.filter(user => user.id !== data.id)
    },
    delete_group: function (data) {
      console.log('Recieved delete group event')
      this.groups = this.groups.filter(group => group.id !== data.id)
    }
  },
  methods: {
    membersInGroup (group) {
      return this.users.filter(user => user.group && user.group.id === group.id).length
    },
    openNewModal () {
      if (this.showingUsers) {
        this.isNewUserModalVisible = true
      } else {
        this.isNewGroupModalVisible = true
      }
    },
    changeUserGroup (userId, value) {
      this.ApiPut(`users/${userId}/group`, value ? { id: parseInt(value) } : {})
        .then(() => Vue.noty.success(`Successfully changed user's group.`))
    },
    editGroup (group) {
      this.editGroupObj = group
      this.isEditGroupModalVisible = true
    },
    resendEmail (user) {
      this.ApiPost(`/users/${user.id}/resend-email`)
        .then(() => Vue.noty.success(`Re-sent registration email to ${user.email}`))
    },
    confirmRevokeUser (user) {
      this.revokeUserObj = user
      this.isRevokeUserModalVisible = true
    },
    revokeUser (modalAnswer) {
      document.body.classList.remove('modal-open')
      this.isRevokeUserModalVisible = false
      if (modalAnswer) {
        this.ApiDelete(`/users/${this.revokeUserObj.id}`)
          .then(() => Vue.noty.success(`Successfully revoked email.`))
      }
    },
    changeUserStatus (userId, status) {
      this.ApiPut(`/users/${userId}/status`, { status: status })
        .then(() => Vue.noty.success(`Successfully changed user's status.`))
    },
    confirmDeleteGroup (group) {
      this.deleteGroupObj = group
      this.isDeleteGroupModalVisible = true
    },
    deleteGroup (modalAnswer) {
      document.body.classList.remove('modal-open')
      this.isDeleteGroupModalVisible = false
      if (modalAnswer) {
        this.ApiDelete(`/groups/${this.deleteGroupObj.id}`)
          .then(() => Vue.noty.success(`Successfully deleted ${this.deleteGroupObj.name}.`))
      }
    },
    getUsers () {
      Vue.prototype.$api
        .get(`/users`)
        .then(r => r.data)
        .then(users => {
          this.users = users
        })
        .catch((error) => {
          console.log(error)
        })
    },
    getGroups () {
      Vue.prototype.$api
        .get(`/groups`)
        .then(r => r.data)
        .then(groups => {
          this.groups = groups
        })
        .catch((error) => {
          console.log(error)
        })
    },
    ...mapActions('sockets', {
      checkSocketsConnected: 'checkConnected'
    }),
    ...mapActions('user', {
      checkUserLoaded: 'checkLoaded'
    })
  },
  computed: {
    ...mapGetters('sockets', {
      isSocketConnected: 'isConnected'
    }),
    ...mapGetters('user', {
      accessToken: 'getAccessToken',
      user: 'getUser'
    })
  },
  watch: {
    isSocketConnected (value) {
      if (value) {
        this.$socket.client.emit('join_admin')
      }
    }
  },
  async created () {
    this.checkUserLoaded(null)
    this.getUsers()
    this.getGroups()
    if (this.isSocketConnected) {
      this.$socket.client.emit('join_admin')
    } else {
      this.checkSocketsConnected(null)
      this.$socket.client.emit('join_admin')
    }
  }
}
</script>
