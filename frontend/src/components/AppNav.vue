<template>
  <div class="app-nav">
    <router-link to="/" class="nav-logo" aria-label="智能旅行助手首页">
      <GlassIcon name="logo" />
    </router-link>
    <nav class="nav-links" aria-label="主导航">
      <router-link to="/" class="nav-item" :class="{ active: isHome }" aria-label="创建行程" title="创建行程">
        <GlassIcon name="grid" />
        <span>创建行程</span>
      </router-link>
      <router-link to="/history" class="nav-item" :class="{ active: isHistory }" aria-label="历史行程" title="历史行程">
        <GlassIcon name="history" />
        <span>历史行程</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import GlassIcon from '@/components/GlassIcon.vue'

const route = useRoute()
const isHome = computed(() => route.path === '/')
const isHistory = computed(() => route.path.startsWith('/history'))
</script>
