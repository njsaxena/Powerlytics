import React from 'react'
import { 
  BoltIcon, 
  ExclamationTriangleIcon,
  ChartBarIcon,
  HomeIcon,
  WrenchScrewdriverIcon,
  LightBulbIcon,
  CpuChipIcon
} from '@heroicons/react/24/outline'

interface DeviceCardProps {
  device: {
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
  isSelected: boolean
  predictions: Array<{
    timestamp: string
    predicted_power_w: number
    confidence?: number
  }>
  onSelect: () => void
}

export default function DeviceCard({ device, isSelected, predictions, onSelect }: DeviceCardProps) {
  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType.toLowerCase()) {
      case 'electrical_panel':
        return BoltIcon
      case 'hvac':
        return HomeIcon
      case 'workshop':
        return WrenchScrewdriverIcon
      case 'lighting':
        return LightBulbIcon
      case 'appliances':
        return CpuChipIcon
      default:
        return ChartBarIcon
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'active':
        return 'status-normal'
      case 'warning':
        return 'status-warning'
      case 'error':
        return 'status-error'
      default:
        return 'status-normal'
    }
  }

  const formatPower = (power?: number) => {
    if (!power) return 'N/A'
    return `${power.toFixed(0)}W`
  }

  const formatEnergy = (energy?: number) => {
    if (!energy) return 'N/A'
    if (energy >= 1000) {
      return `${(energy / 1000).toFixed(1)} kWh`
    }
    return `${energy.toFixed(0)} Wh`
  }

  const DeviceIcon = getDeviceIcon(device.device_type)
  const hasAnomalies = (device.anomalies_last_24h || 0) > 0
  const nextPrediction = predictions[0]

  return (
    <div
      className={`card cursor-pointer transition-all duration-200 hover:shadow-lg ${
        isSelected ? 'ring-2 ring-primary-500 shadow-lg' : ''
      }`}
      onClick={onSelect}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${
            isSelected ? 'bg-primary-100' : 'bg-gray-100'
          }`}>
            <DeviceIcon className={`h-6 w-6 ${
              isSelected ? 'text-primary-600' : 'text-gray-600'
            }`} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{device.device_name}</h3>
            <p className="text-sm text-gray-500">{device.location}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`status-indicator ${getStatusColor(device.status)}`}>
            {device.status}
          </span>
          {hasAnomalies && (
            <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />
          )}
        </div>
      </div>

      {/* Current Power */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Current Power</span>
          <span className="text-lg font-semibold text-gray-900">
            {formatPower(device.current_power)}
          </span>
        </div>
        {device.avg_power_last_24h && (
          <div className="text-xs text-gray-500 mt-1">
            Avg 24h: {formatPower(device.avg_power_last_24h)}
          </div>
        )}
      </div>

      {/* Energy Today */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Energy Today</span>
          <span className="text-sm font-medium text-gray-900">
            {formatEnergy(device.total_energy_today)}
          </span>
        </div>
      </div>

      {/* Next Prediction */}
      {nextPrediction && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-600">Next Hour Prediction</span>
            <span className="text-sm font-medium text-gray-900">
              {formatPower(nextPrediction.predicted_power_w)}
            </span>
          </div>
          {nextPrediction.confidence && (
            <div className="text-xs text-gray-500 mt-1">
              Confidence: {(nextPrediction.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      )}

      {/* Anomalies */}
      {hasAnomalies && (
        <div className="flex items-center space-x-2 text-red-600">
          <ExclamationTriangleIcon className="h-4 w-4" />
          <span className="text-sm font-medium">
            {device.anomalies_last_24h} anomal{device.anomalies_last_24h !== 1 ? 'ies' : 'y'} detected
          </span>
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{device.device_type.replace('_', ' ')}</span>
          <span>ID: {device.device_id}</span>
        </div>
      </div>
    </div>
  )
}
