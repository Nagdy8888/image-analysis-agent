import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone", // for Docker: copies minimal server + static assets
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/uploads/**" },
      { protocol: "http", hostname: "127.0.0.1", port: "8000", pathname: "/uploads/**" },
    ],
  },
};

export default nextConfig;
