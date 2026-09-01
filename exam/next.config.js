/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',          // ← MUHIM: Docker uchun
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '8002',
        pathname: '/media/**',
      },
    ],
  },
};

module.exports = nextConfig;