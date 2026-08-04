import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import './styles/glass.css'
import App from './App.vue'
import Home from './views/Home.vue'
import Result from './views/Result.vue'
import History from './views/History.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/result',
      redirect: '/history'
    },
    {
      path: '/result/:id',
      name: 'Result',
      component: Result
    },
    {
      path: '/history',
      name: 'History',
      component: History
    }
  ]
})

const app = createApp(App)

app.use(router)
app.use(createPinia())
app.use(Antd)

app.mount('#app')
