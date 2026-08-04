<template>
  <section class="trip-map">
    <div class="map-header">
      <h2>
        <GlassIcon name="map" class="head-icon" />
        行程地图
      </h2>
      <div class="map-legend">
        <span v-for="item in legendItems" :key="item.label" class="legend-item">
          <i class="legend-dot" :style="{ background: item.color }"></i>
          {{ item.label }}
        </span>
        <span v-if="hasHotel" class="legend-item">
          <i class="legend-dot" style="background: #94a3b8"></i>
          住宿
        </span>
      </div>
    </div>
    <div ref="mapContainer" class="map-container">
      <a-spin
        v-if="status === 'loading'"
        tip="地图加载中..."
        class="map-spin"
      />
      <div v-else-if="status === 'error'" class="map-error">{{ errorMsg }}</div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import GlassIcon from '@/components/GlassIcon.vue'
import type { TripPlan } from '@/types'

const props = defineProps<{ plan: TripPlan | null }>()

interface MapPoint {
  dayIndex: number
  name: string
  address: string
  longitude: number
  latitude: number
  visitDuration?: number
  imageUrl?: string
  isHotel?: boolean
  label?: string
}

const mapContainer = ref<HTMLElement | null>(null)
const status = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const errorMsg = ref('')

let map: any = null
let markers: any[] = []
let infoWindow: any = null
let geocodeMarker: any = null

const DAY_COLORS = [
  '#ffcf7d',
  '#9be8e2',
  '#ffb19a',
  '#c3a6ff',
  '#8fd0ff',
  '#c5f28a',
  '#ff9ec7',
  '#ffd166'
]

const points = computed<MapPoint[]>(() => {
  if (!props.plan) return []
  const result: MapPoint[] = []
  props.plan.days.forEach((day) => {
    day.attractions.forEach((attraction) => {
      if (isValidLocation(attraction.location.longitude, attraction.location.latitude)) {
        result.push({
          dayIndex: day.day_index,
          name: attraction.name,
          address: attraction.address,
          longitude: attraction.location.longitude,
          latitude: attraction.location.latitude,
          visitDuration: attraction.visit_duration,
          imageUrl: attraction.image_url
        })
      }
    })
    if (
      day.hotel?.location &&
      isValidLocation(day.hotel.location.longitude, day.hotel.location.latitude)
    ) {
      result.push({
        dayIndex: day.day_index,
        name: day.hotel.name,
        address: day.hotel.address,
        longitude: day.hotel.location.longitude,
        latitude: day.hotel.location.latitude,
        isHotel: true
      })
    }
  })
  return result
})

const legendItems = computed(() => {
  const seen = new Map<number, string>()
  points.value.forEach((point) => {
    if (!point.isHotel && !seen.has(point.dayIndex)) {
      seen.set(point.dayIndex, DAY_COLORS[point.dayIndex % DAY_COLORS.length])
    }
  })
  return Array.from(seen.entries()).map(([dayIndex, color]) => ({
    label: `第${dayIndex + 1}天`,
    color
  }))
})

const hasHotel = computed(() => points.value.some((point) => point.isHotel))

function isValidLocation(longitude?: number, latitude?: number): boolean {
  return (
    typeof longitude === 'number' &&
    typeof latitude === 'number' &&
    Number.isFinite(longitude) &&
    Number.isFinite(latitude) &&
    Math.abs(longitude) <= 180 &&
    Math.abs(latitude) <= 90 &&
    !(longitude === 0 && latitude === 0)
  )
}

function escapeHtml(value: string): string {
  const entities: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }
  return value.replace(/[&<>"']/g, (char) => entities[char])
}

function buildMarkerContent(point: MapPoint, color: string): HTMLElement {
  const el = document.createElement('div')
  el.style.background = color
  el.style.border = '2px solid #ffffff'
  el.style.borderRadius = '50%'
  el.style.width = '28px'
  el.style.height = '28px'
  el.style.display = 'flex'
  el.style.alignItems = 'center'
  el.style.justifyContent = 'center'
  el.style.color = '#10202a'
  el.style.fontSize = '12px'
  el.style.fontWeight = '700'
  el.style.boxShadow = '0 4px 14px rgba(4, 16, 24, 0.45)'
  el.textContent = point.label || (point.isHotel ? '宿' : String(point.dayIndex + 1))
  return el
}

async function initMap() {
  if (!mapContainer.value) return
  destroyMap()

  const key = String(
    import.meta.env.VITE_AMAP_WEB_JS_KEY || import.meta.env.VITE_AMAP_WEB_KEY || ''
  )
  if (!key) {
    status.value = 'error'
    errorMsg.value = '未配置高德地图 Key'
    return
  }

  status.value = 'loading'
  try {
    const loadConfig: any = {
      key,
      version: '2.0',
      plugins: ['AMap.Scale', 'AMap.ToolBar', 'AMap.InfoWindow', 'AMap.Geocoder']
    }
    const securityCode = String(import.meta.env.VITE_AMAP_SECURITY_CODE || '')
    if (securityCode) loadConfig.securityJsCode = securityCode

    const AMap = await AMapLoader.load(loadConfig)
    map = new AMap.Map(mapContainer.value, {
      zoom: 11,
      resizeEnable: true
    })
    map.addControl(new AMap.Scale())
    map.addControl(new AMap.ToolBar({ position: 'RB' }))
    infoWindow = new AMap.InfoWindow({ offset: new AMap.Pixel(0, -34), autoMove: true })
    renderPoints(AMap)
    status.value = 'ready'
  } catch (err: any) {
    status.value = 'error'
    errorMsg.value = `地图加载失败: ${err?.message || err}`
    destroyMap()
  }
}

function renderPoints(AMap: any) {
  const valid = points.value
  if (valid.length) {
    valid.forEach((point) => {
      const color = point.isHotel
        ? '#94a3b8'
        : DAY_COLORS[point.dayIndex % DAY_COLORS.length]
      const marker = new AMap.Marker({
        position: new AMap.LngLat(point.longitude, point.latitude),
        content: buildMarkerContent(point, color),
        offset: new AMap.Pixel(-14, -14),
        title: point.name
      })
      marker.on('click', () => openInfo(AMap, point))
      map.add(marker)
      markers.push(marker)
    })
    map.setFitView(markers, false, [48, 48, 48, 48], 1200)
  } else if (props.plan?.city) {
    geocodeCity(AMap, props.plan.city)
  } else {
    map.setZoomAndCenter(11, new AMap.LngLat(116.397428, 39.90923))
  }
}

function openInfo(AMap: any, point: MapPoint) {
  const image = point.imageUrl
    ? `<img class="map-info-image" src="${point.imageUrl}" alt="${escapeHtml(point.name)}" />`
    : ''
  const duration = point.visitDuration
    ? `<p class="map-info-meta">${point.visitDuration} 分钟</p>`
    : ''
  const tag = point.isHotel
    ? '<span class="map-info-tag map-info-tag-hotel">住宿</span>'
    : `<span class="map-info-tag">第${point.dayIndex + 1}天</span>`
  const content = `
    <div class="map-info">
      ${image}
      <div class="map-info-body">
        <strong>${escapeHtml(point.name)}</strong>
        <p>${escapeHtml(point.address || '')}</p>
        ${duration}
        ${tag}
      </div>
    </div>`
  infoWindow.setContent(content)
  infoWindow.open(map, new AMap.LngLat(point.longitude, point.latitude))
}

function geocodeCity(AMap: any, city: string) {
  AMap.plugin('AMap.Geocoder', () => {
    const geocoder = new AMap.Geocoder({ city, radius: 1000 })
    geocoder.getLocation(city, (geocodeStatus: string, result: any) => {
      const location = result?.geocodes?.[0]?.location
      if (geocodeStatus === 'complete' && location) {
        geocodeMarker = new AMap.Marker({
          position: location,
          content: buildMarkerContent(
            {
              dayIndex: 0,
              name: city,
              address: '',
              longitude: location.lng,
              latitude: location.lat,
              label: '城'
            },
            '#ffcf7d'
          ),
          offset: new AMap.Pixel(-14, -14),
          title: city
        })
        map.add(geocodeMarker)
        map.setZoomAndCenter(12, location)
      } else {
        map.setZoomAndCenter(11, new AMap.LngLat(116.397428, 39.90923))
      }
    })
  })
}

function destroyMap() {
  if (infoWindow) {
    infoWindow.close()
    infoWindow = null
  }
  markers.forEach((marker) => {
    marker.setMap(null)
  })
  markers = []
  if (geocodeMarker) {
    geocodeMarker.setMap(null)
    geocodeMarker = null
  }
  if (map) {
    map.destroy()
    map = null
  }
}

watch(
  () => props.plan,
  () => {
    if (props.plan) initMap()
  },
  { immediate: true, flush: 'post' }
)

onMounted(() => {
  if (status.value === 'idle' && props.plan) initMap()
})

onBeforeUnmount(destroyMap)
</script>

<style scoped>
.head-icon {
  width: calc(19 * var(--u));
  height: calc(19 * var(--u));
  margin-right: calc(7 * var(--u));
  color: var(--amber);
  vertical-align: calc(-3 * var(--u));
}

.map-spin {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.map-error {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: calc(20 * var(--u));
  color: rgba(255, 255, 255, 0.75);
  font-size: calc(14 * var(--u));
  text-align: center;
}
</style>

<style>
.map-info {
  width: 240px;
  background: rgba(10, 26, 35, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 14px;
  overflow: hidden;
  font-family: 'Inter', 'Noto Sans SC', -apple-system, 'Segoe UI', Roboto, sans-serif;
  color: #fff;
}

.map-info-image {
  display: block;
  width: 100%;
  height: 128px;
  object-fit: cover;
}

.map-info-body {
  padding: 12px 14px 14px;
}

.map-info-body strong {
  display: block;
  color: #fff;
  font-size: 14px;
  line-height: 1.4;
}

.map-info-body p {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  line-height: 1.5;
}

.map-info-meta {
  display: inline-block;
  margin: 8px 8px 0 0 !important;
  color: rgba(255, 255, 255, 0.85) !important;
}

.map-info-tag {
  display: inline-block;
  margin-top: 8px;
  padding: 3px 9px;
  border-radius: 999px;
  background: rgba(255, 207, 125, 0.2);
  color: #ffcf7d;
  font-size: 12px;
}

.map-info-tag-hotel {
  background: rgba(155, 232, 226, 0.18);
  color: #9be8e2;
}
</style>
