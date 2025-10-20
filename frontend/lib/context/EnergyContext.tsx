import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { energyApi } from '../api'

// Types
export interface Device {
  device_id: string
  device_name: string
  device_type: string
  location: string
  current_power?: number
  total_energy_today?: number
  avg_power_last_24h?: number
  anomalies_last_24h?: number
  status: string
}

export interface Anomaly {
  device_id: string
  timestamp: string
  type: string
  severity: string
  original_power?: number
  anomaly_power?: number
  confidence?: number
}

export interface Prediction {
  timestamp: string
  predicted_power_w: number
  confidence?: number
  confidence_interval_lower?: number
  confidence_interval_upper?: number
}

export interface ChatMessage {
  id: string
  message: string
  response?: string
  confidence?: number
  sources?: Array<{
    type: string
    description: string
    timestamp: string
  }>
  recommendations?: Array<{
    type: string
    title: string
    description: string
    action: string
    potential_savings: string
  }>
  timestamp: string
  isUser: boolean
}

export interface DashboardData {
  summary: {
    total_devices: number
    total_energy_wh: number
    anomalies_count: number
    last_updated: string
  }
  devices: Device[]
  trends: Array<{
    hour_ts: string
    avg_power: number
    total_energy: number
  }>
  recent_anomalies: Anomaly[]
}

// State interface
interface EnergyState {
  devices: Device[]
  dashboardData: DashboardData | null
  selectedDevice: string | null
  predictions: Record<string, Prediction[]>
  anomalies: Anomaly[]
  chatMessages: ChatMessage[]
  loading: boolean
  error: string | null
}

// Action types
type EnergyAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_DEVICES'; payload: Device[] }
  | { type: 'SET_DASHBOARD_DATA'; payload: DashboardData }
  | { type: 'SET_SELECTED_DEVICE'; payload: string | null }
  | { type: 'SET_PREDICTIONS'; payload: { deviceId: string; predictions: Prediction[] } }
  | { type: 'SET_ANOMALIES'; payload: Anomaly[] }
  | { type: 'ADD_CHAT_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_CHAT_MESSAGES'; payload: ChatMessage[] }

// Initial state
const initialState: EnergyState = {
  devices: [],
  dashboardData: null,
  selectedDevice: null,
  predictions: {},
  anomalies: [],
  chatMessages: [],
  loading: false,
  error: null,
}

// Reducer
function energyReducer(state: EnergyState, action: EnergyAction): EnergyState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload }
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false }
    case 'SET_DEVICES':
      return { ...state, devices: action.payload }
    case 'SET_DASHBOARD_DATA':
      return { ...state, dashboardData: action.payload }
    case 'SET_SELECTED_DEVICE':
      return { ...state, selectedDevice: action.payload }
    case 'SET_PREDICTIONS':
      return {
        ...state,
        predictions: {
          ...state.predictions,
          [action.payload.deviceId]: action.payload.predictions,
        },
      }
    case 'SET_ANOMALIES':
      return { ...state, anomalies: action.payload }
    case 'ADD_CHAT_MESSAGE':
      return {
        ...state,
        chatMessages: [...state.chatMessages, action.payload],
      }
    case 'SET_CHAT_MESSAGES':
      return { ...state, chatMessages: action.payload }
    default:
      return state
  }
}

// Context
const EnergyContext = createContext<{
  state: EnergyState
  dispatch: React.Dispatch<EnergyAction>
  actions: {
    refreshData: () => Promise<void>
    getPredictions: (deviceId: string, horizonHours?: number) => Promise<void>
    getAnomalies: (deviceId?: string) => Promise<void>
    sendChatMessage: (message: string, deviceId?: string) => Promise<void>
    selectDevice: (deviceId: string | null) => void
  }
} | null>(null)

// Provider component
export function EnergyProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(energyReducer, initialState)

  // Actions
  const refreshData = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      dispatch({ type: 'SET_ERROR', payload: null })

      const dashboardData = await energyApi.getDashboardData()
      dispatch({ type: 'SET_DASHBOARD_DATA', payload: dashboardData })
      dispatch({ type: 'SET_DEVICES', payload: dashboardData.devices })
      dispatch({ type: 'SET_ANOMALIES', payload: dashboardData.recent_anomalies })
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error instanceof Error ? error.message : 'Unknown error' })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const getPredictions = async (deviceId: string, horizonHours = 24) => {
    try {
      const predictions = await energyApi.getPredictions(deviceId, horizonHours)
      dispatch({ type: 'SET_PREDICTIONS', payload: { deviceId, predictions } })
    } catch (error) {
      console.error('Failed to get predictions:', error)
    }
  }

  const getAnomalies = async (deviceId?: string) => {
    try {
      const anomalies = await energyApi.getAnomalies(deviceId)
      dispatch({ type: 'SET_ANOMALIES', payload: anomalies })
    } catch (error) {
      console.error('Failed to get anomalies:', error)
    }
  }

  const sendChatMessage = async (message: string, deviceId?: string) => {
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message,
      timestamp: new Date().toISOString(),
      isUser: true,
    }

    dispatch({ type: 'ADD_CHAT_MESSAGE', payload: userMessage })

    try {
      const response = await energyApi.sendChatMessage(message, deviceId)
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: response.response,
        response: response.response,
        confidence: response.confidence,
        sources: response.sources,
        recommendations: response.recommendations,
        timestamp: new Date().toISOString(),
        isUser: false,
      }

      dispatch({ type: 'ADD_CHAT_MESSAGE', payload: aiMessage })
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        isUser: false,
      }
      dispatch({ type: 'ADD_CHAT_MESSAGE', payload: errorMessage })
    }
  }

  const selectDevice = (deviceId: string | null) => {
    dispatch({ type: 'SET_SELECTED_DEVICE', payload: deviceId })
  }

  const actions = {
    refreshData,
    getPredictions,
    getAnomalies,
    sendChatMessage,
    selectDevice,
  }

  return (
    <EnergyContext.Provider value={{ state, dispatch, actions }}>
      {children}
    </EnergyContext.Provider>
  )
}

// Hook to use the context
export function useEnergy() {
  const context = useContext(EnergyContext)
  if (!context) {
    throw new Error('useEnergy must be used within an EnergyProvider')
  }
  return context
}
