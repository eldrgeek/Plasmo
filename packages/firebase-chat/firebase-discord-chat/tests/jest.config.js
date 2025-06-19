module.exports = {
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/setup.js'],
  testMatch: [
    '<rootDir>/unit/**/*.test.js',
    '<rootDir>/integration/**/*.test.js'
  ],
  collectCoverageFrom: [
    '../src/**/*.{js,jsx}',
    '!../src/index.js',
    '!../src/reportWebVitals.js',
    '!../src/setupTests.js'
  ],
  coverageDirectory: '<rootDir>/coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  transform: {
    '^.+\\.(js|jsx)$': 'babel-jest'
  },
  transformIgnorePatterns: [
    'node_modules/(?!(firebase|@firebase)/)'
  ],
  testTimeout: 30000,
  clearMocks: true,
  verbose: true
}; 