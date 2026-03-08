/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  outDir: "out",
  basePath: "/News3",
  assetPrefix: "/News3/",
  images: {
    unoptimized: true,
  },
};

module.exports = nextConfig;
