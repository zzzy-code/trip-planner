import axios from 'axios'
import type { ApiResponse, TripFormData, TripPlan, TripRecord } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const photoCache = new Map<string, string>()

export function getStreamUrl(formData: TripFormData): string {
  const params = encodeURIComponent(JSON.stringify(formData))
  return `${API_BASE_URL}/api/trips/plan/stream?params=${params}`
}

export async function listTrips(page = 1, size = 10): Promise<ApiResponse<TripRecord[]>> {
  const response = await apiClient.get<ApiResponse<TripRecord[]>>('/api/trips', {
    params: { page, size }
  })
  return response.data
}

export async function getTripById(id: string): Promise<ApiResponse<TripRecord>> {
  const response = await apiClient.get<ApiResponse<TripRecord>>(`/api/trips/${id}`)
  return response.data
}

export async function updateTripById(id: string, plan: TripPlan): Promise<ApiResponse<TripRecord>> {
  const response = await apiClient.put<ApiResponse<TripRecord>>(`/api/trips/${id}`, plan)
  return response.data
}

export async function deleteTripById(id: string): Promise<ApiResponse<{ deleted: boolean }>> {
  const response = await apiClient.delete<ApiResponse<{ deleted: boolean }>>(`/api/trips/${id}`)
  return response.data
}

export async function getAttractionPhoto(name: string, city = ''): Promise<string | null> {
  const key = city ? `${city}:${name}` : name
  if (photoCache.has(key)) {
    return photoCache.get(key) || null
  }
  const response = await apiClient.get('/api/poi/photo', {
    params: city ? { name, city } : { name }
  })
  const url = (response.data?.data?.photo_url as string | undefined) || ''
  if (url) photoCache.set(key, url)
  return url || null
}

export default apiClient
