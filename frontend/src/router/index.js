import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import(/* webpackChunkName: "about" */ '../views/Login.vue'),
    meta: {
      title: _ => 'Login',
      requiresAuth: false
    }
  },
  {
    path: '/',
    alias: '/deployments',
    name: 'deployments',
    component: () => import(/* webpackChunkName: "about" */ '../views/Deployments.vue'),
    meta: {
      title: _ => 'Deployments',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/incidents',
    name: 'incidents',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incidents.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      return props
    },
    meta: {
      title: _ => 'All Incidents',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/assigned-incidents',
    name: 'assignedIncidents',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incidents.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      return props
    },
    meta: {
      title: _ => 'Assigned Incidents',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/closed-incidents',
    name: 'closedIncidents',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incidents.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      return props
    },
    meta: {
      title: _ => 'Closed Incidents',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/incidents/:incidentName-:incidentId(\\d+)',
    name: 'incident',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incident.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      props.incidentId = +props.incidentId
      return props
    },
    meta: {
      title: route => route.params.incidentName.replace('-', ' '),
      requiresAuth: true
    }
  },
  {
    path: '/notifications',
    name: 'notifications',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incident.vue'),
    meta: {
      title: _ => 'Notifications',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/map',
    name: 'map',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incident.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      return props
    },
    meta: {
      title: _ => 'Map',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/live-feed',
    name: 'liveFeed',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incident.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      return props
    },
    meta: {
      title: _ => 'Live Feed',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/decision-making-log',
    name: 'decisionMakingLog',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incident.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      return props
    },
    meta: {
      title: _ => 'Decision-Making Log',
      requiresAuth: true
    }
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/actions-required',
    name: 'actionsRequired',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incident.vue'),
    props (route) {
      const props = { ...route.params }
      props.deploymentId = +props.deploymentId
      return props
    },
    meta: {
      title: _ => 'Actions Required',
      requiresAuth: true
    }
  },
  {
    path: '/404',
    alias: '*',
    name: 'PageNotFound',
    component: () => import(/* webpackChunkName: "about" */ '../views/PageNotFound.vue'),
    props: true,
    meta: {
      title: _ => 'Page Not Found',
      requiresAuth: false
    }
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta && to.meta.title ? to.meta.title(to) : 'DGVOST'
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (localStorage.getItem('accessToken') == null) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
  next()
})

export default router
