import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import SurveyPage from './pages/SurveyPage.vue'
import AdminPage from './pages/AdminPage.vue'
import AdminLogin from './pages/AdminLogin.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/survey' },
    { path: '/survey', component: SurveyPage },
    { path: '/admin/login', component: AdminLogin },
    {
      path: '/admin',
      component: AdminPage,
      beforeEnter: (to, from, next) => {
        if (localStorage.getItem('admin_auth') === 'true') next()
        else next('/admin/login')
      }
    }
  ]
})

createApp(App).use(router).mount('#app')
