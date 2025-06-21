'use client'

import { useState } from 'react'
import { Search, Plus, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

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
  personal: 'bg-blue-100 text-blue-800 border-blue-200',
  work: 'bg-green-100 text-green-800 border-green-200',
  learning: 'bg-purple-100 text-purple-800 border-purple-200',
  project: 'bg-orange-100 text-orange-800 border-orange-200',
  insight: 'bg-pink-100 text-pink-800 border-pink-200'
}

const sourceColors = {
  cursor: 'bg-gray-100 text-gray-800 border-gray-200',
  chatgpt: 'bg-teal-100 text-teal-800 border-teal-200',
  manual: 'bg-yellow-100 text-yellow-800 border-yellow-200'
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

  const filteredMemories = mockMemories.filter(memory => {
    const matchesSearch = memory.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         memory.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCategory = selectedCategory === 'all' || memory.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Memory Dashboard</h2>
          <p className="text-gray-600">Manage and explore your AI memory collection</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Memory
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search memories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md bg-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        >
          <option value="all">All Categories</option>
          <option value="personal">Personal</option>
          <option value="work">Work</option>
          <option value="learning">Learning</option>
          <option value="project">Project</option>
          <option value="insight">Insight</option>
        </select>
      </div>

      {/* Memory Cards */}
      <div className="grid gap-4">
        {filteredMemories.map((memory) => (
          <Card key={memory.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <Badge className={categoryColors[memory.category]}>
                    {memory.category}
                  </Badge>
                  <Badge variant="outline" className={sourceColors[memory.source]}>
                    {memory.source}
                  </Badge>
                  <Badge variant="outline">
                    {memory.importance}/10
                  </Badge>
                </div>
                <span className="text-sm text-gray-500">{formatRelativeTime(memory.timestamp)}</span>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-800 mb-3">{memory.content}</p>
              <div className="flex flex-wrap gap-1">
                {memory.tags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">
                    #{tag}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredMemories.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No memories found matching your criteria.</p>
        </div>
      )}
    </div>
  )
} 