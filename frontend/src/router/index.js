import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    alias: '/deployments',
    name: 'deployments',
    component: () => import(/* webpackChunkName: "about" */ '../views/Deployments.vue')
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/incidents',
    name: 'viewIncidents',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incidents.vue')
  },
  {
    path: '/deployments/:deploymentName-:deploymentId(\\d+)/incidents/:incidentName-:incidentId(\\d+)',
    name: 'viewIncident',
    component: () => import(/* webpackChunkName: "about" */ '../views/Incident.vue')
  },
  {
    path: '/404',
    alias: '*',
    name: 'PageNotFound',
    component: () => import(/* webpackChunkName: "about" */ '../views/PageNotFound.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
