/** @type {import('next').NextConfig} */
const isGitHubActions = process.env.GITHUB_ACTIONS === 'true';
const repositoryName = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? '';
const configuredBasePath = process.env.NEXT_PUBLIC_BASE_PATH;
const basePath = configuredBasePath ?? (isGitHubActions && repositoryName ? `/${repositoryName}` : '');

const nextConfig = {
  output: 'export',
  reactStrictMode: true,
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  basePath,
  assetPrefix: basePath ? `${basePath}/` : undefined,
};

module.exports = nextConfig;
