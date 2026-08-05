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
            <button
              v-if="!editMode"
              type="button"
              class="cta-btn ghost"
              :disabled="!!exportingType"
              @click="exportImage"
            >
              <GlassIcon name="pic" />
              {{ exportingType === 'image' ? '导出中...' : '导出长图' }}
            </button>

            <button
              v-if="!editMode"
              type="button"
              class="cta-btn ghost"
              :disabled="!!exportingType"
              @click="exportPDF"
            >
              <GlassIcon name="save" />
              {{ exportingType === 'pdf' ? '导出中...' : '导出PDF' }}
            </button>

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

        <!-- 导出专用的完整行程容器 (支持跨天完整导出) -->
        <div v-if="isExporting" ref="exportContent" class="export-container">
          <div class="export-header">
            <div class="export-title">
              <h1>{{ plan.city }} · 行程计划</h1>
              <p>{{ plan.start_date }} 至 {{ plan.end_date }} (共 {{ plan.days.length }} 天)</p>
            </div>
            <div v-if="plan.budget" class="export-budget">
              <span>预估总预算：<b>¥{{ plan.budget.total }}</b></span>
            </div>
          </div>

          <div v-if="plan.overall_suggestions" class="export-suggestions">
            <h3>行程总览与建议</h3>
            <p>{{ plan.overall_suggestions }}</p>
          </div>

          <div v-for="day in plan.days" :key="day.day_index" class="export-day-card">
            <div class="export-day-head">
              <h2>第 {{ day.day_index + 1 }} 天</h2>
              <span class="export-date">{{ day.date }}</span>
            </div>
            <p class="day-desc">{{ day.description }}</p>
            <div class="hotel-line">
              <span class="mini-tag accent">住宿：{{ day.hotel?.name || day.accommodation || '住宿待定' }}</span>
              <span class="mini-tag">交通：{{ day.transportation || '混合交通' }}</span>
            </div>

            <h3 class="section-label">景点推荐</h3>
            <div class="attraction-grid">
              <div v-for="item in day.attractions" :key="item.name" class="attraction-card">
                <div v-if="item.image_url" class="attraction-media">
                  <img :src="item.image_url" :alt="item.name" />
                </div>
                <div class="attraction-body">
                  <h4>{{ item.name }}</h4>
                  <p class="addr">{{ item.address }}</p>
                  <p class="desc">{{ item.description }}</p>
                  <div class="attraction-meta">
                    <span class="mini-tag">{{ item.visit_duration }} 分钟</span>
                    <span v-if="item.ticket_price" class="mini-tag accent">¥{{ item.ticket_price }}</span>
                    <span v-if="item.rating" class="mini-tag">★ {{ item.rating }}</span>
                  </div>
                </div>
              </div>
            </div>

            <h3 class="section-label">餐饮安排</h3>
            <div class="meal-row">
              <div v-for="meal in day.meals" :key="meal.type" class="meal-chip">
                <span class="meal-name">
                  {{ meal.type === 'breakfast' ? '早餐' : meal.type === 'lunch' ? '午餐' : meal.type === 'dinner' ? '晚餐' : '推荐' }}：
                  <b>{{ meal.name }}</b>
                </span>
                <span v-if="meal.description || meal.address" class="meal-desc">{{ meal.description || meal.address }}</span>
                <span v-if="meal.estimated_cost" class="cost">¥{{ meal.estimated_cost }}</span>
              </div>
            </div>
          </div>
        </div>
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
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
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

const isExporting = ref(false)
const exportingType = ref<'image' | 'pdf' | null>(null)
const exportContent = ref<HTMLElement | null>(null)

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

  // 将新获取的图片URL持久化到数据库，避免后续查看时再次调用 API
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

async function prepareCanvas() {
  isExporting.value = true
  await nextTick()
  await new Promise((resolve) => setTimeout(resolve, 300))

  if (!exportContent.value) {
    throw new Error('导出节点构建失败')
  }

  return await html2canvas(exportContent.value, {
    scale: 2,
    useCORS: true,
    allowTaint: true,
    backgroundColor: '#07141b',
    logging: false
  })
}

async function exportImage() {
  if (!plan.value || exportingType.value) return
  exportingType.value = 'image'
  const hide = message.loading('正在生成行程长图...', 0)
  try {
    const canvas = await prepareCanvas()
    const image = canvas.toDataURL('image/png')
    const link = document.createElement('a')
    link.href = image
    link.download = `行程计划_${plan.value.city}_${plan.value.start_date}.png`
    link.click()
    message.success('行程长图导出成功！')
  } catch (err: any) {
    console.error('导出长图失败:', err)
    message.error('导出长图失败，请重试')
  } finally {
    isExporting.value = false
    exportingType.value = null
    hide()
  }
}

async function exportPDF() {
  if (!plan.value || exportingType.value) return
  exportingType.value = 'pdf'
  const hide = message.loading('正在生成行程 PDF 文件...', 0)
  try {
    const canvas = await prepareCanvas()
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgWidth = 210
    const pageHeight = 297
    const imgHeight = (canvas.height * imgWidth) / canvas.width
    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
    heightLeft -= pageHeight

    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
    }

    pdf.save(`行程计划_${plan.value.city}_${plan.value.start_date}.pdf`)
    message.success('PDF 导出成功！')
  } catch (err: any) {
    console.error('导出 PDF 失败:', err)
    message.error('导出 PDF 失败，请重试')
  } finally {
    isExporting.value = false
    exportingType.value = null
    hide()
  }
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

/* 导出专用容器与样式 */
.export-container {
  position: absolute;
  left: -9999px;
  top: 0;
  width: 880px;
  padding: 36px;
  background: #07141b;
  color: #ffffff;
  font-family: var(--font-ui);
  box-sizing: border-box;
}

.export-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2px solid rgba(255, 207, 125, 0.3);
  padding-bottom: 18px;
  margin-bottom: 24px;
}

.export-title h1 {
  font-size: 32px;
  color: #ffcf7d;
  font-family: var(--font-art);
  margin: 0 0 8px 0;
}

.export-title p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  font-size: 14px;
}

.export-budget {
  font-size: 16px;
  color: #ffcf7d;
}

.export-suggestions {
  background: rgba(255, 207, 125, 0.1);
  border-left: 4px solid #ffcf7d;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 28px;
}

.export-suggestions h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #ffcf7d;
}

.export-suggestions p {
  margin: 0;
  font-size: 13.5px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.9);
}

.export-day-card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 28px;
}

.export-day-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.export-day-head h2 {
  font-size: 22px;
  color: #ffcf7d;
  margin: 0;
  font-family: var(--font-art);
}

.export-date {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
}

.meal-name b {
  color: #ffffff;
}

.meal-desc {
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  margin-left: 8px;
}
</style>
