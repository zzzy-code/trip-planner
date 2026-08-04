<template>
  <div class="page result-page">
    <a-spin :spinning="loading">
      <template v-if="plan">
        <div class="result-toolbar">
          <button type="button" class="cta-btn ghost" @click="router.push('/history')">
            <GlassIcon name="arrow" />
            返回历史
          </button>
          <div class="toolbar-actions">
            <button v-if="!editMode" type="button" class="cta-btn ghost" @click="startEdit">
              <GlassIcon name="edit" />
              编辑行程
            </button>
            <template v-else>
              <button type="button" class="cta-btn" @click="save">
                <GlassIcon name="save" />
                保存
              </button>
              <button type="button" class="cta-btn ghost" @click="cancel">
                <GlassIcon name="close" />
                取消
              </button>
            </template>
          </div>
        </div>

        <section class="result-hero">
          <div>
            <span class="chip">
              <GlassIcon name="spark" />
              行程总览
            </span>
            <h1>{{ plan.city }}</h1>
            <p class="dates">{{ plan.start_date }} 至 {{ plan.end_date }} · {{ plan.days.length }} 天</p>
            <a-textarea
              v-if="editMode"
              v-model:value="plan.overall_suggestions"
              :rows="3"
              style="margin-top: 14px"
            />
            <p v-else class="suggestions">{{ plan.overall_suggestions }}</p>
          </div>
          <div v-if="plan.budget" class="budget-block">
            <span class="budget-label">总预算</span>
            <div class="budget-number">
              <i>¥</i>{{ plan.budget.total }}
            </div>
            <div class="budget-metrics">
              <div class="metric">
                <b>{{ plan.budget.total_attractions }}</b>
                <span>景点</span>
              </div>
              <div class="metric">
                <b>{{ plan.budget.total_hotels }}</b>
                <span>住宿</span>
              </div>
              <div class="metric">
                <b>{{ plan.budget.total_meals }}</b>
                <span>餐饮</span>
              </div>
              <div class="metric">
                <b>{{ plan.budget.total_transportation }}</b>
                <span>交通</span>
              </div>
            </div>
          </div>
        </section>

        <div class="result-grid">
          <div class="result-main">
            <div class="day-tabs">
              <button
                v-for="day in plan.days"
                :key="day.day_index"
                type="button"
                class="day-tab"
                :class="{ on: activeDay === day.day_index }"
                @click="activeDay = day.day_index"
              >
                第 {{ day.day_index + 1 }} 天
              </button>
            </div>

            <section v-if="currentDay" class="day-card">
              <div class="day-card-head">
                <h2>第 {{ currentDay.day_index + 1 }} 天</h2>
                <span class="date">{{ currentDay.date }}</span>
              </div>
              <a-textarea
                v-if="editMode"
                v-model:value="currentDay.description"
                :rows="2"
                style="margin-top: 14px"
              />
              <p v-else class="day-desc">{{ currentDay.description }}</p>

              <div class="hotel-line">
                <span class="mini-tag accent">
                  <GlassIcon name="bed" />
                  {{ currentDay.hotel?.name || currentDay.accommodation || '住宿待定' }}
                </span>
                <span class="mini-tag">
                  <GlassIcon name="walk" />
                  {{ currentDay.transportation || '混合交通' }}
                </span>
                <span v-if="currentDay.hotel?.address" class="mini-tag">
                  {{ currentDay.hotel.address }}
                </span>
              </div>

              <h3 class="section-label">
                <GlassIcon name="pin" />
                景点
              </h3>
              <div class="attraction-grid">
                <article
                  v-for="item in currentDay.attractions"
                  :key="item.name"
                  class="attraction-card"
                >
                  <div class="attraction-media">
                    <img
                      v-if="item.image_url"
                      :src="item.image_url"
                      :alt="item.name"
                      loading="lazy"
                    />
                    <div v-else class="attraction-placeholder">
                      <GlassIcon name="pic" />
                      <span>图片未找到</span>
                    </div>
                  </div>
                  <div class="attraction-body">
                    <a-input v-if="editMode" v-model:value="item.name" style="margin-bottom: 8px" />
                    <h4 v-else>{{ item.name }}</h4>
                    <p class="addr">{{ item.address }}</p>
                    <a-textarea v-if="editMode" v-model:value="item.description" :rows="2" />
                    <p v-else class="desc">{{ item.description }}</p>
                    <div class="attraction-meta">
                      <span class="mini-tag">{{ item.visit_duration }} 分钟</span>
                      <span v-if="item.ticket_price" class="mini-tag accent">¥{{ item.ticket_price }}</span>
                      <span v-if="item.rating" class="mini-tag">
                        <GlassIcon name="star" />
                        {{ item.rating }}
                      </span>
                    </div>
                  </div>
                </article>
              </div>

              <h3 class="section-label">
                <GlassIcon name="fork" />
                餐饮
              </h3>
              <div class="meal-row">
                <div v-for="meal in currentDay.meals" :key="meal.type" class="meal-chip">
                  <span class="meal-type">
                    <GlassIcon :name="mealIcon(meal.type)" />
                  </span>
                  <div>
                    <b>{{ meal.name }}</b>
                    <span>{{ meal.description || meal.address || '' }}</span>
                  </div>
                  <span v-if="meal.estimated_cost" class="cost">¥{{ meal.estimated_cost }}</span>
                </div>
              </div>
            </section>
          </div>

          <aside class="rail">
            <div v-if="plan.budget" class="card">
              <span class="card-label">
                <GlassIcon name="wallet" />
                预算明细
              </span>
              <div class="budget-rows">
                <div v-for="row in budgetRows" :key="row.label" class="budget-row">
                  <div class="row-top">
                    <b>{{ row.label }}</b>
                    <span>¥{{ row.value }}</span>
                  </div>
                  <div class="bar">
                    <i :style="{ width: `${row.percent}%` }"></i>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="plan.weather_info.length" class="card">
              <span class="card-label">
                <GlassIcon name="sun" />
                天气
              </span>
              <div class="weather-list">
                <div v-for="item in plan.weather_info" :key="item.date" class="weather-item">
                  <span class="w-day">{{ shortDate(item.date) }}</span>
                  <div class="w-info">
                    <b>{{ item.day_weather }}</b>
                    <span>{{ item.wind_direction }} {{ item.wind_power }}</span>
                  </div>
                  <span class="w-temp">{{ item.day_temp }}°</span>
                </div>
              </div>
            </div>

            <div class="card">
              <span class="card-label">
                <GlassIcon name="globe" />
                行程建议
              </span>
              <p class="day-desc note-copy">{{ plan.overall_suggestions }}</p>
            </div>
          </aside>
        </div>

        <section class="map-section">
          <TripMap :plan="plan" />
        </section>
      </template>

      <div v-else-if="!loading" class="empty-wrap">
        <GlassIcon name="map" class="big-icon" />
        <p>没有找到行程</p>
        <button type="button" class="cta-btn ghost" @click="router.push('/history')">返回历史</button>
      </div>
    </a-spin>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import GlassIcon from '@/components/GlassIcon.vue'
import TripMap from '@/components/TripMap.vue'
import { getAttractionPhoto } from '@/services/api'
import { useTripStore } from '@/stores/trip'
import type { Attraction, TripPlan } from '@/types'

const route = useRoute()
const router = useRouter()
const tripStore = useTripStore()
const loading = ref(false)
const editMode = ref(false)
const draft = ref<TripPlan | null>(null)
const original = ref<TripPlan | null>(null)
const activeDay = ref(0)

const plan = computed(() => draft.value)

const currentDay = computed(() => {
  if (!draft.value?.days.length) return undefined
  return (
    draft.value.days.find((day) => day.day_index === activeDay.value) || draft.value.days[0]
  )
})

const budgetRows = computed(() => {
  const budget = draft.value?.budget
  if (!budget) return []
  const total = budget.total || 1
  return [
    { label: '景点门票', value: budget.total_attractions, percent: Math.round((budget.total_attractions / total) * 100) },
    { label: '住宿', value: budget.total_hotels, percent: Math.round((budget.total_hotels / total) * 100) },
    { label: '餐饮', value: budget.total_meals, percent: Math.round((budget.total_meals / total) * 100) },
    { label: '交通', value: budget.total_transportation, percent: Math.round((budget.total_transportation / total) * 100) }
  ]
})

onMounted(load)

async function load() {
  const id = String(route.params.id || '')
  if (!id) return
  loading.value = true
  try {
    const trip = await tripStore.loadTrip(id)
    draft.value = trip.data ? JSON.parse(JSON.stringify(trip.data)) : null
    if (draft.value) await loadAttractionImages()
  } finally {
    loading.value = false
  }
}

async function loadAttractionImages() {
  if (!draft.value) return
  const missing: Attraction[] = []
  draft.value.days.forEach((day) => {
    day.attractions.forEach((attraction) => {
      if (!attraction.image_url) missing.push(attraction)
    })
  })
  if (!missing.length) return

  let next = 0
  let fetched = 0
  async function worker() {
    while (next < missing.length) {
      const attraction = missing[next++]
      try {
        const url = await getAttractionPhoto(attraction.name, draft.value?.city || '')
        if (url) {
          attraction.image_url = url
          fetched++
        }
      } catch {
        // 单张图片获取失败不影响行程展示
      }
    }
  }
  await Promise.all(Array.from({ length: Math.min(3, missing.length) }, () => worker()))

  // 将新获取的图片URL持久化到数据库，避免后续查看时再次调用Unsplash API
  if (fetched > 0) {
    const id = String(route.params.id || '')
    if (id && draft.value) {
      try {
        await tripStore.saveTrip(id, draft.value)
      } catch {
        // 持久化失败不影响当前展示
      }
    }
  }
}

function startEdit() {
  if (!draft.value) return
  original.value = JSON.parse(JSON.stringify(draft.value))
  editMode.value = true
}

function cancel() {
  draft.value = original.value ? JSON.parse(JSON.stringify(original.value)) : draft.value
  editMode.value = false
}

async function save() {
  const id = String(route.params.id || '')
  if (!id || !draft.value) return
  await tripStore.saveTrip(id, draft.value)
  editMode.value = false
  message.success('已保存')
}

function mealIcon(type: string) {
  return (
    {
      breakfast: 'sun',
      lunch: 'fork',
      dinner: 'fork',
      snack: 'drop'
    } as Record<string, string>
  )[type] || 'fork'
}

function shortDate(value: string) {
  const parts = value.split('-')
  return parts.length === 3 ? `${Number(parts[1])}/${Number(parts[2])}` : value
}
</script>

<style scoped>
.note-copy {
  margin-top: calc(12 * var(--u));
  font-size: calc(12.5 * var(--u));
  line-height: calc(19 * var(--u));
  color: rgba(255, 255, 255, 0.8);
}

.mini-tag {
  display: inline-flex;
  align-items: center;
  gap: calc(6 * var(--u));
}

.mini-tag .gicon {
  width: calc(13 * var(--u));
  height: calc(13 * var(--u));
  color: var(--amber);
}

.attraction-media .gicon {
  width: calc(26 * var(--u));
  height: calc(26 * var(--u));
}
</style>
