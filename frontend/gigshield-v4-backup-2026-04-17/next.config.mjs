/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  // Suppress hydration warnings from browser extensions
  reactStrictMode: false,
};

export default nextConfig;
