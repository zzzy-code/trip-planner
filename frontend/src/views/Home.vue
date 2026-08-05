<template>
  <div class="page home-page">
    <section class="home-hero">
      <div class="hero-top">
        <span class="chip">
          <GlassIcon name="spark" />
          智能旅行助手 · AI Trip Concierge
        </span>
        <AppNav />
      </div>
      <h1 class="hero-title">
        <span class="ln"><span>下一站，</span></span>
        <span class="ln"><span>说走就走</span></span>
      </h1>
      <p class="hero-blurb">
        输入目的地、日期与偏好，多智能体会实时规划景点、天气、住宿与每日行程。
      </p>
    </section>

    <div class="home-grid">
      <section class="planner-card">
        <div class="card-head">
          <h2>开始规划</h2>
          <span class="head-note">生成进度实时显示在右侧</span>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="form-grid">
            <div class="field">
              <label class="field-label" for="city">目的地城市</label>
              <input
                id="city"
                v-model.trim="formData.city"
                class="glass-input"
                placeholder="例如：北京、上海、杭州"
                required
              />
            </div>
            <div class="field">
              <label class="field-label">开始日期</label>
              <a-date-picker
                v-model:value="startDate"
                style="width: 100%"
                placeholder="选择开始日期"
                :allow-clear="false"
              />
            </div>
            <div class="field">
              <label class="field-label">结束日期</label>
              <a-date-picker
                v-model:value="endDate"
                style="width: 100%"
                placeholder="选择结束日期"
                :allow-clear="false"
              />
            </div>
          </div>

          <div class="form-grid form-options">
            <div class="field">
              <span class="field-label">交通方式</span>
              <div class="chips">
                <button
                  v-for="opt in transportOptions"
                  :key="opt"
                  type="button"
                  class="chip"
                  :class="{ on: formData.transportation === opt }"
                  @click="formData.transportation = opt"
                >
                  {{ opt }}
                </button>
              </div>
            </div>
            <div class="field">
              <span class="field-label">住宿偏好</span>
              <div class="chips">
                <button
                  v-for="opt in accommodationOptions"
                  :key="opt"
                  type="button"
                  class="chip"
                  :class="{ on: formData.accommodation === opt }"
                  @click="formData.accommodation = opt"
                >
                  {{ opt }}
                </button>
              </div>
            </div>
          </div>

          <div class="field pref-field">
            <span class="field-label">旅行偏好</span>
            <div class="chips">
              <button
                v-for="opt in preferenceOptions"
                :key="opt"
                type="button"
                class="chip"
                :class="{ on: formData.preferences.includes(opt) }"
                @click="togglePreference(opt)"
              >
                {{ opt }}
              </button>
            </div>
          </div>

          <div class="field pref-field">
            <span class="field-label">额外要求</span>
            <textarea
              v-model="formData.free_text_input"
              class="glass-input"
              rows="2"
              placeholder="例如：节奏放慢、避开排队、希望安排博物馆"
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="submit" class="cta-btn" :disabled="tripStore.status === 'running'">
              <GlassIcon name="spark" />
              {{ tripStore.status === 'running' ? '规划中…' : '生成行程' }}
            </button>
            <button type="button" class="cta-btn ghost" @click="router.push('/history')">
              <GlassIcon name="history" />
              历史行程
            </button>
          </div>
        </form>
      </section>

      <aside class="rail">
        <div class="card card-big">
          <span class="card-label">
            <GlassIcon name="pin" />
            下一站
          </span>
          <div class="big-place">{{ previewCity }}</div>
          <div class="metrics">
            <div class="metric">
              <b>{{ previewDays }}</b>
              <span>天行程</span>
            </div>
            <div class="metric">
              <b>{{ formData.preferences.length }}</b>
              <span>项偏好</span>
            </div>
            <div class="metric">
              <b>{{ formData.transportation }}</b>
              <span>交通</span>
            </div>
          </div>
        </div>

        <div class="card">
          <span class="card-label">
            <GlassIcon name="chart" />
            实时进度
          </span>
          <div class="progress-steps">
            <div v-for="step in stepDefs" :key="step.key" class="step-line">
              <span class="step-dot" :class="stepState(step.key)">
                <GlassIcon :name="step.icon" />
              </span>
              <div class="step-text">
                <b>{{ step.label }}</b>
                <span>{{ step.message }}</span>
              </div>
            </div>
          </div>
          <div v-if="tripStore.messages.length" class="event-log">
            <span v-for="(item, index) in tripStore.messages.slice(-5)" :key="index">{{ item }}</span>
          </div>
          <div v-if="tripStore.status === 'error'" class="error-box">{{ tripStore.error }}</div>
        </div>

      </aside>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import type { Dayjs } from 'dayjs'
import GlassIcon from '@/components/GlassIcon.vue'
import AppNav from '@/components/AppNav.vue'
import { useTripStore } from '@/stores/trip'
import type { TripFormData } from '@/types'

const router = useRouter()
const tripStore = useTripStore()
const startDate = ref<Dayjs | null>(null)
const endDate = ref<Dayjs | null>(null)

const transportOptions = ['公共交通', '自驾', '步行', '混合']
const accommodationOptions = ['经济型酒店', '舒适型酒店', '豪华酒店', '民宿']
const preferenceOptions = ['历史文华', '自然风光', '美食', '购物', '艺术', '休闲']

const stepDefs = [
  { key: 'attractions', label: '获取景点', icon: 'pin', message: '使用高德地图搜索目的地景点' },
  { key: 'weather', label: '查询天气', icon: 'sun', message: '获取行程日期内的天气预报' },
  { key: 'hotel', label: '推荐住宿', icon: 'bed', message: '按偏好筛选合适的住宿' },
  { key: 'plan', label: '生成行程', icon: 'spark', message: '智能编排每日路线与预算' }
] as const

const formData = reactive<TripFormData>({
  city: '',
  start_date: '',
  end_date: '',
  travel_days: 1,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  free_text_input: ''
})

const previewCity = computed(() => formData.city || '未选择目的地')
const previewDays = computed(() => formData.travel_days)

watch([startDate, endDate], ([start, end]) => {
  if (!start || !end) return
  const days = end.diff(start, 'day') + 1
  if (days < 1) {
    message.warning('结束日期不能早于开始日期')
    endDate.value = null
    return
  }
  if (days > 30) {
    message.warning('旅行天数不能超过 30 天')
    endDate.value = null
    return
  }
  formData.travel_days = days
})

function togglePreference(option: string) {
  const index = formData.preferences.indexOf(option)
  if (index >= 0) {
    formData.preferences.splice(index, 1)
  } else {
    formData.preferences.push(option)
  }
}

function stepState(key: string) {
  const index = stepDefs.findIndex((item) => item.key === key)
  if (tripStore.status === 'error' && index === tripStore.steps.length) return 'running'
  if (index < tripStore.steps.length) return 'done'
  if (tripStore.status === 'running' && index === tripStore.steps.length) return 'running'
  return ''
}

function handleSubmit() {
  if (!startDate.value || !endDate.value) {
    message.error('请选择完整日期')
    return
  }
  formData.start_date = startDate.value.format('YYYY-MM-DD')
  formData.end_date = endDate.value.format('YYYY-MM-DD')
  tripStore.startGeneration({ ...formData }, (id) => {
    message.success('行程生成成功')
    router.push(`/result/${id}`)
  })
}
</script>

<style scoped>
.home-page {
  min-height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

.form-options {
  margin-top: calc(14 * var(--u));
}

.pref-field {
  margin-top: calc(16 * var(--u));
}

</style>
