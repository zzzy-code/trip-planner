import { defineStore } from 'pinia'
import { getStreamUrl, getTripById, listTrips, updateTripById, deleteTripById } from '@/services/api'
import type { AgentStep, TripFormData, TripPlan, TripRecord } from '@/types'

interface TripState {
  history: TripRecord[]
  status: 'idle' | 'running' | 'success' | 'error'
  steps: AgentStep[]
  messages: string[]
  error: string
  currentEventSource: EventSource | null
  currentTripId: string
  pagination: {
    page: number
    size: number
    total: number
    total_pages: number
  }
}

export const useTripStore = defineStore('trip', {
  state: (): TripState => ({
    history: [],
    status: 'idle',
    steps: [],
    messages: [],
    error: '',
    currentEventSource: null,
    currentTripId: '',
    pagination: {
      page: 1,
      size: 10,
      total: 0,
      total_pages: 0
    }
  }),
  actions: {
    resetProgress() {
      this.status = 'idle'
      this.steps = []
      this.messages = []
      this.error = ''
      this.currentTripId = ''
      if (this.currentEventSource) {
        this.currentEventSource.close()
        this.currentEventSource = null
      }
    },
    startGeneration(formData: TripFormData, onCompleted: (id: string) => void) {
      this.resetProgress()
      this.status = 'running'
      const source = new EventSource(getStreamUrl(formData))
      this.currentEventSource = source

      source.addEventListener('plan_started', (event) => {
        const data = JSON.parse(event.data)
        this.currentTripId = data.trip_plan_id
        this.messages.push('已创建行程任务')
      })

      source.addEventListener('agent_step', (event) => {
        const data = JSON.parse(event.data)
        this.steps.push(data)
        this.messages.push(data.message || data.step_name)
      })

      ;['attraction_found', 'weather_fetched', 'hotel_found', 'plan_generating'].forEach((name) => {
        source.addEventListener(name, (event) => {
          const data = JSON.parse(event.data)
          this.messages.push(data.message || name)
        })
      })

      source.addEventListener('plan_completed', (event) => {
        const data = JSON.parse(event.data)
        this.status = 'success'
        this.currentTripId = data.trip_plan_id
        source.close()
        this.currentEventSource = null
        onCompleted(data.trip_plan_id)
      })

      source.addEventListener('plan_failed', (event) => {
        const data = JSON.parse(event.data)
        this.status = 'error'
        this.error = data.message || '行程生成失败'
        source.close()
        this.currentEventSource = null
      })

      source.onerror = () => {
        if (this.status === 'running') {
          this.status = 'error'
          this.error = 'SSE 连接已断开，请重试'
        }
        source.close()
        this.currentEventSource = null
      }
    },
    async loadHistory(page = 1, size = 10) {
      const result = await listTrips(page, size)
      this.history = result.data
      if (result.meta) this.pagination = result.meta
    },
    async loadTrip(id: string) {
      const result = await getTripById(id)
      return result.data
    },
    async saveTrip(id: string, plan: TripPlan) {
      const result = await updateTripById(id, plan)
      return result.data
    },
    async deleteTrip(id: string) {
      await deleteTripById(id)
      this.history = this.history.filter((item) => item.id !== id)
    }
  }
})
