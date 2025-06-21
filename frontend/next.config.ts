import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Turbopack configuration (stable in 15.3, moved to top-level)
  turbopack: {
    rules: {
      // Custom rules can be added here if needed
    },
  },
  // Enable React 19 features
  reactStrictMode: true,
  // Optimize for modern browsers
  swcMinify: true,
  // Enable TypeScript strict mode
  typescript: {
    ignoreBuildErrors: false,
  },
  // Enable ESLint during builds
  eslint: {
    ignoreDuringBuilds: false,
  },
};

export default nextConfig; 