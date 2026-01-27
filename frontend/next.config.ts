import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  devIndicators: false,
  output: 'standalone',
  outputFileTracingRoot: require('path').join(__dirname),
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'avatars.githubusercontent.com',
      },
    ],
  },
  turbopack: {
    resolveExtensions: ['.tsx', '.ts', '.jsx', '.js', '.mjs', '.json'],
  },
  experimental: {
    optimizeCss: true,
  },
}

export default nextConfig

