import React from 'react'
import { 
  BoltIcon, 
  ExclamationTriangleIcon, 
  ChartBarIcon,
  ClockIcon 
} from '@heroicons/react/24/outline'

interface MetricsOverviewProps {
  data: {
    total_devices: number
    total_energy_wh: number
    anomalies_count: number
    last_updated: string
  }
}

export default function MetricsOverview({ data }: MetricsOverviewProps) {
  const formatEnergy = (wh: number) => {
    if (wh >= 1000) {
      return `${(wh / 1000).toFixed(1)} kWh`
    }
    return `${wh.toFixed(0)} Wh`
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const metrics = [
    {
      name: 'Total Energy Today',
      value: formatEnergy(data.total_energy_wh),
      icon: BoltIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      change: '+12%',
      changeType: 'positive'
    },
    {
      name: 'Active Devices',
      value: data.total_devices.toString(),
      icon: ChartBarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      change: '0%',
      changeType: 'neutral'
    },
    {
      name: 'Anomalies Detected',
      value: data.anomalies_count.toString(),
      icon: ExclamationTriangleIcon,
      color: data.anomalies_count > 0 ? 'text-red-600' : 'text-gray-600',
      bgColor: data.anomalies_count > 0 ? 'bg-red-100' : 'bg-gray-100',
      change: data.anomalies_count > 0 ? 'New' : 'None',
      changeType: data.anomalies_count > 0 ? 'negative' : 'neutral'
    },
    {
      name: 'Last Updated',
      value: formatTime(data.last_updated),
      icon: ClockIcon,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      change: 'Live',
      changeType: 'neutral'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metrics.map((metric) => (
        <div key={metric.name} className="metric-card">
          <div className="flex items-center">
            <div className={`flex-shrink-0 p-3 rounded-lg ${metric.bgColor}`}>
              <metric.icon className={`h-6 w-6 ${metric.color}`} />
            </div>
            <div className="ml-4 flex-1">
              <p className="text-sm font-medium text-gray-600">{metric.name}</p>
              <div className="flex items-baseline">
                <p className="text-2xl font-semibold text-gray-900">{metric.value}</p>
                <span className={`ml-2 text-sm font-medium ${
                  metric.changeType === 'positive' ? 'text-green-600' :
                  metric.changeType === 'negative' ? 'text-red-600' :
                  'text-gray-500'
                }`}>
                  {metric.change}
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
