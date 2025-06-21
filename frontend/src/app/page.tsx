import { Suspense } from 'react'
import { MemoryDashboard } from '@/components/memory/memory-dashboard'
import { PlatformStats } from '@/components/platform/platform-stats'
import { Header } from '@/components/layout/header'
import { LoadingSpinner } from '@/components/ui/loading-spinner'

// This is a Server Component by default in Next.js 15 + React 19
export default async function HomePage() {
  return (
    <main className="container mx-auto px-4 py-8">
      <Header />
      
      <div className="mt-8 space-y-8">
        {/* Platform Statistics */}
        <Suspense fallback={<LoadingSpinner />}>
          <PlatformStats />
        </Suspense>

        {/* Memory Dashboard */}
        <Suspense fallback={<LoadingSpinner />}>
          <MemoryDashboard />
        </Suspense>
      </div>
    </main>
  )
}
