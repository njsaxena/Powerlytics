import React from 'react'
import { 
  UserIcon, 
  SparklesIcon,
  LightBulbIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { format } from 'date-fns'

interface ChatMessageProps {
  message: {
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
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const formatTime = (timestamp: string) => {
    return format(new Date(timestamp), 'h:mm a')
  }

  const getRecommendationIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'energy_saving':
      case 'energy_efficiency':
        return LightBulbIcon
      case 'maintenance':
        return CheckCircleIcon
      case 'immediate_action':
        return ExclamationTriangleIcon
      default:
        return LightBulbIcon
    }
  }

  const getRecommendationColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'energy_saving':
      case 'energy_efficiency':
        return 'text-green-600 bg-green-100'
      case 'maintenance':
        return 'text-blue-600 bg-blue-100'
      case 'immediate_action':
        return 'text-red-600 bg-red-100'
      default:
        return 'text-gray-600 bg-gray-100'
    }
  }

  if (message.isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-xs lg:max-w-md">
          <div className="flex items-end space-x-2">
            <div className="bg-primary-600 text-white px-4 py-2 rounded-lg rounded-br-sm">
              <p className="text-sm">{message.message}</p>
            </div>
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <UserIcon className="h-5 w-5 text-primary-600" />
              </div>
            </div>
          </div>
          <div className="text-xs text-gray-500 mt-1 text-right">
            {formatTime(message.timestamp)}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-xs lg:max-w-2xl">
        <div className="flex items-start space-x-2">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <SparklesIcon className="h-5 w-5 text-purple-600" />
            </div>
          </div>
          <div className="bg-white border border-gray-200 rounded-lg rounded-bl-sm px-4 py-3 shadow-sm">
            <p className="text-sm text-gray-900 mb-2">{message.response || message.message}</p>
            
            {/* Confidence Score */}
            {message.confidence && (
              <div className="flex items-center space-x-2 mb-3">
                <div className="text-xs text-gray-500">Confidence:</div>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${message.confidence * 100}%` }}
                  />
                </div>
                <div className="text-xs text-gray-500">
                  {(message.confidence * 100).toFixed(0)}%
                </div>
              </div>
            )}

            {/* Sources */}
            {message.sources && message.sources.length > 0 && (
              <div className="mb-3">
                <div className="text-xs text-gray-500 mb-1">Sources:</div>
                <div className="space-y-1">
                  {message.sources.map((source, index) => (
                    <div key={index} className="text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded">
                      {source.description}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recommendations */}
            {message.recommendations && message.recommendations.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs text-gray-500 mb-2">Recommendations:</div>
                {message.recommendations.map((rec, index) => {
                  const Icon = getRecommendationIcon(rec.type)
                  return (
                    <div key={index} className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <div className="flex items-start space-x-2">
                        <div className={`p-1 rounded ${getRecommendationColor(rec.type)}`}>
                          <Icon className="h-4 w-4" />
                        </div>
                        <div className="flex-1">
                          <h4 className="text-sm font-medium text-gray-900 mb-1">
                            {rec.title}
                          </h4>
                          <p className="text-xs text-gray-600 mb-2">
                            {rec.description}
                          </p>
                          <div className="flex items-center justify-between">
                            <p className="text-xs text-gray-500">
                              {rec.action}
                            </p>
                            {rec.potential_savings && (
                              <span className="text-xs font-medium text-green-600">
                                {rec.potential_savings}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          {formatTime(message.timestamp)}
        </div>
      </div>
    </div>
  )
}
