import React, { useEffect } from 'react'
import { useEnergy } from '../lib/context/EnergyContext'
import DeviceGrid from './DeviceGrid'
import EnergyChart from './EnergyChart'
import AnomalyList from './AnomalyList'
import MetricsOverview from './MetricsOverview'
import LoadingSpinner from './LoadingSpinner'

export default function Dashboard() {
  const { state, actions } = useEnergy()
  const { dashboardData, loading, error } = state

  useEffect(() => {
    if (!dashboardData) {
      actions.refreshData()
    }
  }, [dashboardData, actions])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner text="Loading dashboard data..." />
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Error Loading Dashboard</h2>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={actions.refreshData}
          className="btn-primary"
        >
          Retry
        </button>
      </div>
    )
  }

  if (!dashboardData) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">No Data Available</h2>
        <p className="text-gray-600 mb-4">Unable to load dashboard data</p>
        <button
          onClick={actions.refreshData}
          className="btn-primary"
        >
          Refresh
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Energy Dashboard</h1>
        <p className="text-gray-600">
          Real-time energy monitoring and AI-powered insights
        </p>
      </div>

      {/* Metrics Overview */}
      <MetricsOverview data={dashboardData.summary} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Energy Chart */}
        <div className="lg:col-span-2">
          <EnergyChart trends={dashboardData.trends} />
        </div>

        {/* Anomalies */}
        <div className="lg:col-span-1">
          <AnomalyList anomalies={dashboardData.recent_anomalies} />
        </div>
      </div>

      {/* Device Grid */}
      <DeviceGrid devices={dashboardData.devices} />
    </div>
  )
}
