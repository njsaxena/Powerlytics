import React, { useState, useRef, useEffect } from 'react'
import { useEnergy } from '../lib/context/EnergyContext'
import ChatMessage from './ChatMessage'
import LoadingSpinner from './LoadingSpinner'
import { 
  PaperAirplaneIcon,
  SparklesIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

export default function ChatInterface() {
  const { state, actions } = useEnergy()
  const { chatMessages, selectedDevice, loading } = state
  const [inputMessage, setInputMessage] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [chatMessages])

  useEffect(() => {
    // Focus input on mount
    inputRef.current?.focus()
  }, [])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!inputMessage.trim() || isTyping) return

    const message = inputMessage.trim()
    setInputMessage('')
    setIsTyping(true)

    try {
      await actions.sendChatMessage(message, selectedDevice || undefined)
    } catch (error) {
      console.error('Failed to send message:', error)
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage(e)
    }
  }

  const suggestedQuestions = [
    "Why was my usage high yesterday?",
    "When is the cheapest time to run my dishwasher?",
    "What's causing the energy spike?",
    "How can I reduce my energy costs?",
    "Show me my energy patterns"
  ]

  const handleSuggestedQuestion = (question: string) => {
    setInputMessage(question)
    inputRef.current?.focus()
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center space-x-2 mb-2">
          <SparklesIcon className="h-8 w-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900">AI Energy Assistant</h1>
        </div>
        <p className="text-gray-600">
          Ask questions about your energy consumption and get AI-powered insights
        </p>
        {selectedDevice && (
          <div className="mt-2 inline-flex items-center px-3 py-1 rounded-full bg-primary-100 text-primary-800 text-sm">
            <span>Analyzing: {selectedDevice}</span>
          </div>
        )}
      </div>

      {/* Chat Container */}
      <div className="card h-96 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto chat-scrollbar p-4 space-y-4">
          {chatMessages.length === 0 ? (
            <div className="text-center py-8">
              <div className="text-gray-400 mb-4">
                <SparklesIcon className="mx-auto h-12 w-12" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to your AI Energy Assistant
              </h3>
              <p className="text-gray-500 mb-6">
                Ask me anything about your energy consumption, anomalies, or optimization tips.
              </p>
              
              {/* Suggested Questions */}
              <div className="space-y-2">
                <p className="text-sm text-gray-600 mb-3">Try asking:</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestedQuestion(question)}
                      className="text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-colors"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {chatMessages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {isTyping && (
                <div className="flex items-center space-x-2 text-gray-500">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm">AI is thinking...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Form */}
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSendMessage} className="flex space-x-3">
            <div className="flex-1">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your energy usage..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
                disabled={isTyping}
              />
            </div>
            <button
              type="submit"
              disabled={!inputMessage.trim() || isTyping}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <PaperAirplaneIcon className="h-4 w-4" />
              <span>Send</span>
            </button>
          </form>
          
          {/* Quick Actions */}
          <div className="mt-3 flex flex-wrap gap-2">
            {suggestedQuestions.slice(0, 3).map((question, index) => (
              <button
                key={index}
                onClick={() => handleSuggestedQuestion(question)}
                className="text-xs px-3 py-1 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors"
                disabled={isTyping}
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="text-center p-4 bg-blue-50 rounded-lg">
          <div className="text-blue-600 mb-2">
            <svg className="mx-auto h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h3 className="text-sm font-medium text-blue-900 mb-1">Real-time Analysis</h3>
          <p className="text-xs text-blue-700">Get instant insights from your live energy data</p>
        </div>
        
        <div className="text-center p-4 bg-green-50 rounded-lg">
          <div className="text-green-600 mb-2">
            <svg className="mx-auto h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-sm font-medium text-green-900 mb-1">Smart Recommendations</h3>
          <p className="text-xs text-green-700">AI-powered suggestions to optimize your energy usage</p>
        </div>
        
        <div className="text-center p-4 bg-purple-50 rounded-lg">
          <div className="text-purple-600 mb-2">
            <ExclamationTriangleIcon className="mx-auto h-6 w-6" />
          </div>
          <h3 className="text-sm font-medium text-purple-900 mb-1">Anomaly Detection</h3>
          <p className="text-xs text-purple-700">Automatic detection of unusual energy patterns</p>
        </div>
      </div>
    </div>
  )
}
