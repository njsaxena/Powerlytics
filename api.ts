import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const energyApi = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Get dashboard data
  async getDashboardData() {
    const response = await api.get('/dashboard')
    return response.data
  },

  // Get devices
  async getDevices() {
    const response = await api.get('/devices')
    return response.data.devices
  },

  // Get device current usage
  async getCurrentUsage(deviceId: string) {
    const response = await api.get(`/devices/${deviceId}/current`)
    return response.data
  },

  // Get device history
  async getUsageHistory(deviceId: string, hours = 24) {
    const response = await api.get(`/devices/${deviceId}/history`, {
      params: { hours }
    })
    return response.data
  },

  // Get predictions
  async getPredictions(deviceId: string, horizonHours = 24) {
    const response = await api.post('/predict', {
      device_id: deviceId,
      horizon_hours: horizonHours,
      include_confidence: true
    })
    return response.data.predictions
  },

  // Get anomalies
  async getAnomalies(deviceId?: string, since?: string, severity?: string) {
    const params: any = {}
    if (deviceId) params.device_id = deviceId
    if (since) params.since = since
    if (severity) params.severity = severity

    const response = await api.get('/anomalies', { params })
    return response.data.anomalies
  },

  // Send chat message
  async sendChatMessage(message: string, deviceId?: string) {
    const response = await api.post('/chat', {
      message,
      device_id: deviceId
    })
    return response.data
  },

  // Get recommendations
  async getRecommendations(deviceId: string) {
    const response = await api.get(`/recommendations/${deviceId}`)
    return response.data.recommendations
  }
}

export default api
