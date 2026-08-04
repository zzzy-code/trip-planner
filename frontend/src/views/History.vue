<template>
  <div class="page history-page">
    <div class="page-head">
      <div class="head-block">
        <div class="head-top">
          <span class="chip">
            <GlassIcon name="history" />
            行程档案
          </span>
          <AppNav />
        </div>
        <h1><span class="ln"><span>历史行程</span></span></h1>
        <p>所有已生成行程会保存到数据库，可再次查看、分享或删除。</p>
      </div>
      <button type="button" class="cta-btn" @click="router.push('/')">
        <GlassIcon name="plus" />
        创建新行程
      </button>
    </div>

    <a-spin :spinning="loading">
      <div v-if="!loading && tripStore.history.length === 0" class="empty-wrap">
        <GlassIcon name="map" class="big-icon" />
        <p>暂无历史行程</p>
        <button type="button" class="cta-btn" @click="router.push('/')">去创建行程</button>
      </div>

      <div v-else class="history-grid">
        <article
          v-for="trip in tripStore.history"
          :key="trip.id"
          class="history-card"
          @click="router.push(`/result/${trip.id}`)"
        >
          <span class="status-badge mini-tag" :class="statusClass(trip.status)">
            {{ statusText(trip.status) }}
          </span>
          <h3>{{ trip.city }}</h3>
          <p class="dates">{{ trip.start_date }} 至 {{ trip.end_date }} · {{ trip.travel_days }} 天</p>
          <p class="created">创建于 {{ formatTime(trip.created_at) }}</p>
          <div class="history-actions" @click.stop>
            <button type="button" class="cta-btn ghost" @click="router.push(`/result/${trip.id}`)">
              <GlassIcon name="eye" />
              查看
            </button>
            <a-popconfirm
              title="确认删除这个行程？"
              @confirm="removeTrip(trip.id)"
            >
              <button type="button" class="cta-btn ghost danger">
                <GlassIcon name="close" />
                删除
              </button>
            </a-popconfirm>
          </div>
        </article>
      </div>

      <a-pagination
        v-if="tripStore.pagination.total > tripStore.pagination.size"
        class="pager"
        :current="tripStore.pagination.page"
        :page-size="tripStore.pagination.size"
        :total="tripStore.pagination.total"
        @change="load"
      />
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import GlassIcon from '@/components/GlassIcon.vue'
import AppNav from '@/components/AppNav.vue'
import { useTripStore } from '@/stores/trip'

const router = useRouter()
const tripStore = useTripStore()
const loading = ref(false)

onMounted(() => load(1))

async function load(page = 1) {
  loading.value = true
  try {
    await tripStore.loadHistory(page, 10)
  } finally {
    loading.value = false
  }
}

async function removeTrip(id: string) {
  await tripStore.deleteTrip(id)
  message.success('已删除')
}

function statusClass(status: string) {
  if (status === 'completed') return 'accent'
  if (status === 'failed') return 'danger'
  return ''
}

function statusText(status: string) {
  if (status === 'completed') return '已完成'
  if (status === 'failed') return '失败'
  return '生成中'
}

function formatTime(value?: string) {
  return value ? new Date(value).toLocaleString() : '-'
}
</script>

<style scoped>
.mini-tag {
  display: inline-flex;
  align-items: center;
  gap: calc(6 * var(--u));
}

.mini-tag.danger {
  border-color: rgba(255, 140, 125, 0.42);
  background: rgba(255, 110, 95, 0.14);
  color: #ffb9ad;
}

.cta-btn.danger {
  border-color: rgba(255, 140, 125, 0.42);
  background: rgba(255, 110, 95, 0.14);
}

.cta-btn.danger:hover {
  background: rgba(255, 110, 95, 0.26);
}

.cta-btn .gicon {
  width: calc(17 * var(--u));
  height: calc(17 * var(--u));
}
</style>
