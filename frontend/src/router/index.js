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
    path: '/deployments/:deploymentName-:deploymentId/incidents',
    name: 'viewIncidents',
    props: (route) => {
      const deploymentId = Number.parseInt(route.params.deploymentId, 10)
      if (Number.isNaN(deploymentId)) {
        return 0
      }
      return { deploymentId }
    },
    component: () => import(/* webpackChunkName: "about" */ '../views/Incidents.vue')
  },
  {
    path: '*',
    component: () => import(/* webpackChunkName: "about" */ '../views/PageNotFound.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
