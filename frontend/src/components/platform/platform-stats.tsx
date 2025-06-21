import { Database, Zap, TrendingUp, Users } from 'lucide-react'

// Mock data for demonstration - in real app this would come from API
const stats = [
  {
    label: 'Total Memories',
    value: '2,847',
    change: '+12%',
    icon: Database,
    color: 'from-blue-500 to-cyan-500'
  },
  {
    label: 'Active Sessions',
    value: '23',
    change: '+5%',
    icon: Zap,
    color: 'from-purple-500 to-pink-500'
  },
  {
    label: 'Sync Rate',
    value: '98.5%',
    change: '+0.3%',
    icon: TrendingUp,
    color: 'from-green-500 to-emerald-500'
  },
  {
    label: 'Connected Users',
    value: '156',
    change: '+8%',
    icon: Users,
    color: 'from-orange-500 to-red-500'
  }
]

export async function PlatformStats() {
  // Simulate async data fetching
  await new Promise(resolve => setTimeout(resolve, 100))
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <div
            key={index}
            className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-6 hover:bg-white/15 transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-3 bg-gradient-to-br ${stat.color} rounded-xl`}>
                <Icon className="h-6 w-6 text-white" />
              </div>
              <span className="text-green-400 text-sm font-medium">
                {stat.change}
              </span>
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white mb-1">
                {stat.value}
              </h3>
              <p className="text-gray-300 text-sm">
                {stat.label}
              </p>
            </div>
          </div>
        )
      })}
    </div>
  )
} 