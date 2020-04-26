import Vue from 'vue'
import Router from 'vue-router'
// import dashboard from '@/view/index/dashboard'
// import NavMent from '@/components/NavMent'
// import index from '@/view/index/index'
// import detail from '@/view/index/detail'

// const index = () => import('@/view/index/index')
// const task = () => import('@/view/task/task')
// const dashboard = () => import('@/view/index/index')
Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/vuln',
      name: 'vuln',
      meta: {name: '漏洞管理'},
      // component: NavMent
      component: () => import('@/view/index/vuln')
    },
    {
      path: '/',
      name: 'tasks',
      meta: {name: '任务管理'},
      // component: () => import('@/view/task/task')
      component: () => import('@/view/task/taskIndex')
    },
    {
      path: '/task/:task_id',
      name: 'taskDetail',
      component: () => import('@/view/task/taskDetail')
    },
    {
      path: '/task/targets/:task_id',
      name: 'taskTargets',
      component: () => import('@/view/task/taskTargets')
    },
    {
      path: '/poc',
      name: 'poc',
      meta: {name: 'POC'},
      component: () => import('@/view/poc/poc')
    },
    {
      path: '/devices',
      name: 'devices',
      meta: {name: '资产管理'},
      component: () => import('@/view/device/index')
    },
    {
      path: '/group',
      name: 'group',
      meta: {name: '分组管理'},
      component: () => import('@/view/group/index')
    },
    {
      path: '/group/:tag_name',
      name: 'tagDetail',
      meta: {name: '分组详情'},
      component: () => import('@/view/group/tagDetail')
    },
    {
      path: '/group/targets/:tag_name',
      name: 'groupTargets',
      component: () => import('@/view/group/groupHosts')
    },
    {
      path: '/settings',
      name: 'settings',
      meta: {name: '设置'},
      component: () => import('@/view/settings/index')
    }
    // {
    //   path: '/dashboard',
    //   name: 'dashboard',
    //   component: dashboard
    // }
  ]
})
