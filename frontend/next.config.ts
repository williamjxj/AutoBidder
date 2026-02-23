import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  images: {
    domains: [],
  },
  env: {
    PYTHON_AI_SERVICE_URL: process.env.PYTHON_AI_SERVICE_URL,
  },
}

export default nextConfig
