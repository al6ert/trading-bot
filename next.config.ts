import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Suppress hydration warnings caused by browser extensions (wallets)
  reactStrictMode: true,
  
  // Empty turbopack config to silence the warning
  // Turbopack handles extension conflicts better than webpack by default
  turbopack: {},
};

export default nextConfig;
