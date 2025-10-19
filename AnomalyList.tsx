import React from 'react'
import { 
  ExclamationTriangleIcon,
  ClockIcon,
  BoltIcon
} from '@heroicons/react/24/outline'

interface AnomalyListProps {
  anomalies: Array<{
    device_id: string
    timestamp: string
    type: string
    severity: string
    original_power?: number
    anomaly_power?: number
    confidence?: number
  }>
}

export default function AnomalyList({ anomalies }: AnomalyListProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'text-red-600 bg-red-100'
      case 'medium':
        return 'text-yellow-600 bg-yellow-100'
      case 'low':
        return 'text-blue-600 bg-blue-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'power_spike':
      case 'spike':
        return BoltIcon
      case 'trend':
        return ChartBarIcon
      case 'seasonal':
        return ClockIcon
      default:
        return ExclamationTriangleIcon
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) {
      return 'Just now'
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`
    } else {
      return date.toLocaleDateString()
    }
  }

  const formatPower = (power?: number) => {
    if (!power) return 'N/A'
    return `${power.toFixed(0)}W`
  }

  if (anomalies.length === 0) {
    return (
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Anomalies</h3>
          <span className="text-sm text-gray-500">Last 24h</span>
        </div>
        <div className="text-center py-8">
          <div className="text-green-500 mb-2">
            <svg className="mx-auto h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <p className="text-sm text-gray-500">No anomalies detected</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Anomalies</h3>
        <span className="text-sm text-gray-500">{anomalies.length} detected</span>
      </div>
      
      <div className="space-y-3 max-h-96 overflow-y-auto scrollbar-hide">
        {anomalies.map((anomaly, index) => {
          const TypeIcon = getTypeIcon(anomaly.type)
          const powerIncrease = anomaly.anomaly_power && anomaly.original_power 
            ? ((anomaly.anomaly_power - anomaly.original_power) / anomaly.original_power * 100)
            : 0

          return (
            <div
              key={`${anomaly.device_id}-${anomaly.timestamp}-${index}`}
              className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${getSeverityColor(anomaly.severity)}`}>
                  <TypeIcon className="h-4 w-4" />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {anomaly.type.replace('_', ' ')}
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${getSeverityColor(anomaly.severity)}`}>
                      {anomaly.severity}
                    </span>
                  </div>
                  
                  <div className="mt-1 text-xs text-gray-500">
                    Device: {anomaly.device_id}
                  </div>
                  
                  {anomaly.anomaly_power && anomaly.original_power && (
                    <div className="mt-2 text-sm">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-600">Power:</span>
                        <div className="flex items-center space-x-2">
                          <span className="text-gray-900">
                            {formatPower(anomaly.original_power)}
                          </span>
                          <span className="text-gray-400">→</span>
                          <span className="text-red-600 font-medium">
                            {formatPower(anomaly.anomaly_power)}
                          </span>
                          {powerIncrease > 0 && (
                            <span className="text-red-600 text-xs">
                              (+{powerIncrease.toFixed(0)}%)
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                      <ClockIcon className="h-3 w-3" />
                      <span>{formatTimestamp(anomaly.timestamp)}</span>
                    </div>
                    {anomaly.confidence && (
                      <span>
                        {(anomaly.confidence * 100).toFixed(0)}% confidence
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      {anomalies.length > 5 && (
        <div className="mt-4 text-center">
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
            View all anomalies
          </button>
        </div>
      )}
    </div>
  )
}
