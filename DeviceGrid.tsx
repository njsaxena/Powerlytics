import React from 'react'
import { useEnergy } from '../lib/context/EnergyContext'
import DeviceCard from './DeviceCard'
import LoadingSpinner from './LoadingSpinner'

interface DeviceGridProps {
  devices: Array<{
    device_id: string
    device_name: string
    device_type: string
    location: string
    current_power?: number
    total_energy_today?: number
    avg_power_last_24h?: number
    anomalies_last_24h?: number
    status: string
  }>
}

export default function DeviceGrid({ devices }: DeviceGridProps) {
  const { state, actions } = useEnergy()
  const { selectedDevice, predictions, loading } = state

  const handleDeviceSelect = (deviceId: string) => {
    actions.selectDevice(deviceId)
    // Load predictions for the selected device
    actions.getPredictions(deviceId)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner text="Loading devices..." />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Devices</h2>
        <div className="text-sm text-gray-500">
          {devices.length} device{devices.length !== 1 ? 's' : ''} connected
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices.map((device) => (
          <DeviceCard
            key={device.device_id}
            device={device}
            isSelected={selectedDevice === device.device_id}
            predictions={predictions[device.device_id] || []}
            onSelect={() => handleDeviceSelect(device.device_id)}
          />
        ))}
      </div>

      {devices.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Devices Connected</h3>
          <p className="text-gray-500">Connect your energy monitoring devices to get started.</p>
        </div>
      )}
    </div>
  )
}
