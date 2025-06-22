import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Enable React strict mode for better development experience
  reactStrictMode: true,
  
  // Use SWC minifier for better performance
  swcMinify: true,
  
  // TypeScript configuration
  typescript: {
    ignoreBuildErrors: false,
  },
  
  // ESLint configuration  
  eslint: {
    ignoreDuringBuilds: false,
  },

  // Image optimization
  images: {
    unoptimized: true, // For better compatibility with Vercel
  },

  // Output configuration for static export compatibility
  output: 'standalone',
};

export default nextConfig; 