'use client'

import { useState } from 'react'
import { Search, Filter, Brain, Tag, Clock, Star, BarChart3, Map, RefreshCw } from 'lucide-react'

// Types for Memory Management
interface Memory {
  id: string
  content: string
  category: 'personal' | 'work' | 'learning' | 'project' | 'insight'
  timestamp: string
  source: 'cursor' | 'chatgpt' | 'manual'
  tags: string[]
  importance: number
}

// Mock data with static timestamps
const mockMemories: Memory[] = [
  {
    id: '1',
    content: 'User prefers clean, modular code architecture with well-separated concerns',
    category: 'personal',
    source: 'cursor',
    timestamp: '2025-06-21T20:00:00.000Z',
    tags: ['preference', 'architecture', 'code-style'],
    importance: 9
  },
  {
    id: '2', 
    content: 'Memory Orchestration Platform successfully deployed with Next.js 15 and React 19',
    category: 'project',
    source: 'cursor',
    timestamp: '2025-06-21T19:00:00.000Z',
    tags: ['deployment', 'nextjs', 'react'],
    importance: 10
  },
  {
    id: '3',
    content: 'Latest stable versions: Next.js 15.3.4 and React 19.1.0 are production ready',
    category: 'learning',
    source: 'chatgpt',
    timestamp: '2025-06-21T18:00:00.000Z',
    tags: ['nextjs', 'react', 'versions', 'stable'],
    importance: 8
  },
  {
    id: '4',
    content: 'React 19 introduces Server Components and improved Suspense patterns',
    category: 'learning',
    source: 'manual',
    timestamp: '2025-06-21T17:00:00.000Z',
    tags: ['react19', 'server-components', 'suspense'],
    importance: 9
  }
]

const categoryColors = {
  personal: 'from-blue-500 to-blue-600',
  work: 'from-green-500 to-green-600',
  learning: 'from-purple-500 to-purple-600',
  project: 'from-orange-500 to-orange-600',
  insight: 'from-pink-500 to-pink-600'
}

function formatRelativeTime(date: string): string {
  const now = new Date()
  const then = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (diffInSeconds < 60) return "just now"
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
  
  return new Date(date).toLocaleDateString()
}

export function MemoryDashboard() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const handleMemoryMap = () => {
    alert('Memory Map: This will open an interactive D3.js visualization showing memory relationships and clusters')
  }

  const handleMemoryAnalytics = () => {
    alert('Memory Analytics: Detailed insights about memory patterns, trends, and usage statistics')
  }

  const handleRefreshMemories = () => {
    alert('Refresh Memories: Sync latest memories from all connected sources and update the dashboard')
  }

  const filteredMemories = mockMemories.filter(memory => {
    const matchesSearch = memory.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         memory.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || memory.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-white/20">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Memory Dashboard</h2>
              <p className="text-gray-300 text-sm">
                {filteredMemories.length} memories found
              </p>
            </div>
          </div>

          {/* Dashboard CTAs */}
          <div className="flex items-center space-x-2">
            <button 
              onClick={handleMemoryMap}
              className="flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 rounded-lg transition-all duration-300 text-white text-sm font-medium"
            >
              <Map className="h-4 w-4" />
              <span>Memory Map</span>
            </button>
            
            <button 
              onClick={handleMemoryAnalytics}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors"
              title="Memory Analytics"
            >
              <BarChart3 className="h-4 w-4 text-white" />
            </button>
            
            <button 
              onClick={handleRefreshMemories}
              className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors group"
              title="Refresh Memories"
            >
              <RefreshCw className="h-4 w-4 text-white group-hover:rotate-180 transition-transform duration-500" />
            </button>
          </div>
        </div>

        {/* Search and Filter */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search memories..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="pl-10 pr-8 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 appearance-none"
            >
              <option value="all">All Categories</option>
              <option value="personal">Personal</option>
              <option value="work">Work</option>
              <option value="learning">Learning</option>
              <option value="project">Project</option>
              <option value="insight">Insight</option>
            </select>
          </div>
        </div>
      </div>

      {/* Memory List */}
      <div className="p-6">
        {/* Debug info */}
        <div className="mb-4 text-xs text-gray-400">
          Debug: Total memories: {mockMemories.length}, Filtered: {filteredMemories.length}, Search: &quot;{searchTerm}&quot;, Category: {selectedCategory}
        </div>

        <div className="space-y-4">
          {filteredMemories.map((memory) => (
            <div
              key={memory.id}
              className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all duration-300 cursor-pointer"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-white mb-3 leading-relaxed">
                    {memory.content}
                  </p>
                  
                  <div className="flex flex-wrap items-center gap-2">
                    {/* Category Badge */}
                    <div className={`px-3 py-1 bg-gradient-to-r ${categoryColors[memory.category]} rounded-full`}>
                      <span className="text-white text-xs font-medium">
                        {memory.category}
                      </span>
                    </div>
                    
                    {/* Source Badge */}
                    <div className="px-3 py-1 bg-white/10 border border-white/20 rounded-full">
                      <span className="text-gray-300 text-xs font-medium">
                        {memory.source}
                      </span>
                    </div>
                    
                    {/* Tags */}
                    {memory.tags.slice(0, 3).map((tag) => (
                      <div key={tag} className="flex items-center space-x-1 px-2 py-1 bg-white/5 rounded-full">
                        <Tag className="h-3 w-3 text-gray-400" />
                        <span className="text-gray-400 text-xs">
                          {tag}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="text-right ml-6 flex-shrink-0">
                  <div className="flex items-center space-x-1 text-gray-400 text-sm mb-2">
                    <Clock className="h-4 w-4" />
                    <span>{formatRelativeTime(memory.timestamp)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 text-yellow-400" />
                    <span className="text-yellow-400 text-sm font-medium">
                      {memory.importance}/10
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {filteredMemories.length === 0 && (
          <div className="text-center py-12">
            <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">No memories found</p>
            <p className="text-gray-500 text-sm">Try adjusting your search or filter criteria</p>
          </div>
        )}
      </div>
    </div>
  )
} 