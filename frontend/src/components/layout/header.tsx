'use client'

import { Brain, Settings, BarChart3, Plus, RefreshCw, Download } from 'lucide-react'

export function Header() {
  const handleAddMemory = () => {
    alert('Add Memory: This will open a form to manually add a new memory to the platform')
  }

  const handleAnalytics = () => {
    alert('Analytics Dashboard: This will show detailed memory insights, trends, and usage statistics')
  }

  const handleSettings = () => {
    alert('Settings: Configure sync preferences, API connections, and platform settings')
  }

  const handleRefresh = () => {
    alert('Refresh: Sync latest memories from all connected sources (Cursor, ChatGPT, etc.)')
  }

  const handleExport = () => {
    alert('Export: Download memories in various formats (JSON, CSV, PDF)')
  }

  return (
    <header className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-blue-600 rounded-xl">
            <Brain className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">
              Memory Orchestration Platform
            </h1>
            <p className="text-gray-300 text-sm">
              Advanced AI Memory Management System
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {/* Add Memory CTA */}
          <button 
            onClick={handleAddMemory}
            className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 rounded-lg transition-all duration-300 text-white font-medium"
          >
            <Plus className="h-4 w-4" />
            <span>Add Memory</span>
          </button>

          {/* Refresh CTA */}
          <button 
            onClick={handleRefresh}
            className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors group"
            title="Refresh Memories"
          >
            <RefreshCw className="h-5 w-5 text-white group-hover:rotate-180 transition-transform duration-500" />
          </button>

          {/* Export CTA */}
          <button 
            onClick={handleExport}
            className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            title="Export Memories"
          >
            <Download className="h-5 w-5 text-white" />
          </button>

          {/* Analytics CTA */}
          <button 
            onClick={handleAnalytics}
            className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            title="Analytics Dashboard"
          >
            <BarChart3 className="h-5 w-5 text-white" />
          </button>

          {/* Settings CTA */}
          <button 
            onClick={handleSettings}
            className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
            title="Settings"
          >
            <Settings className="h-5 w-5 text-white" />
          </button>

          <div className="px-3 py-1 bg-green-500/20 border border-green-500/30 rounded-full">
            <span className="text-green-300 text-sm font-medium">● Connected</span>
          </div>
        </div>
      </div>
    </header>
  )
} 