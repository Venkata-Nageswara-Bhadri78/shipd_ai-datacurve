FROM --platform=linux/arm64 node:20-slim

# Create a directory for the package.json
WORKDIR /config

# Initialize npm and install Jest locally
RUN npm init -y && \
    npm install --save-dev -g jest

# Update package.json with exact configuration
RUN node -e "const pkg = { \
  name: 'app', \
  version: '1.0.0', \
  type: 'module', \
  scripts: { \
    test: 'NODE_OPTIONS=\"\$NODE_OPTIONS --no-warnings --experimental-vm-modules\" npx jest /app' \
  }, \
  keywords: [], \
  author: '', \
  license: 'ISC', \
  description: '', \
  jest: { \
    transform: {}, \
    moduleFileExtensions: ['mjs', 'js'], \
    testMatch: ['**/test.solution.mjs'], \
    rootDir: '/' \
  } \
}; \
require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2))"

# Create app directory for mounted files
WORKDIR /app

# The actual solution files will be mounted at runtime
CMD ["sh", "-c", "cd /config && npm test"] 