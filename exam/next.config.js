/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  
  // Image optimization'ni o'chirish (sharp kerak emas)
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;