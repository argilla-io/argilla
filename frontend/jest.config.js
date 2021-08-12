module.exports = {
  // tell Jest to handle `*.vue` files
  moduleFileExtensions: ["js", "json", "vue"],
  watchman: false,
  moduleNameMapper: {
    "assets/(.*)": "<rootDir>/assets/$1",
    "^~/(.*)$": "<rootDir>/$1",
    "^~~/(.*)$": "<rootDir>/$1",
    "^@/(.*)$": "<rootDir>/$1"
  },
  transform: {
    // process js with `babel-jest`
    "^.+\\.js$": "<rootDir>/node_modules/babel-jest",
    // process `*.vue` files with `vue-jest`
    ".*\\.(vue)$": "<rootDir>/node_modules/vue-jest"
  },
  snapshotSerializers: ["<rootDir>/node_modules/jest-serializer-vue"],
  collectCoverage: true,
  testEnvironment: "jsdom",
  collectCoverageFrom: [
    "<rootDir>/components/**/*.vue",
    "<rootDir>/pages/*.vue"
  ],
  setupFiles: ["<rootDir>/jest.setup.js"],
};