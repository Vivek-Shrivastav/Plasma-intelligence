/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**.r2.dev" },
      { protocol: "https", hostname: "**.amazonaws.com" },
      { protocol: "http", hostname: "localhost" },
    ],
  },
};

module.exports = nextConfig;
