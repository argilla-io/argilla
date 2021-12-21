module.exports = {
  // tell Jest to handle `*.vue` files
  moduleFileExtensions: ["js", "json", "vue"],
  watchman: false,
  moduleNameMapper: {
    "assets/(.*)": "<rootDir>/assets/$1",
    "^~/(.*)$": "<rootDir>/$1",
    "^~~/(.*)$": "<rootDir>/$1",
    "^@/(.*)$": "<rootDir>/$1",
  },
  // Disable integration tests for now
  modulePathIgnorePatterns: ["<rootDir>/cypress"],
  transform: {
    // process js with `babel-jest`
    "^.+\\.js$": "babel-jest",
    "^.+\\.vue$": "vue-jest",
  },
  snapshotSerializers: ["<rootDir>/node_modules/jest-serializer-vue"],
  collectCoverage: true,
  testEnvironment: "jsdom",
  collectCoverageFrom: [
    "<rootDir>/components/**/*.vue",
    "<rootDir>/pages/*.vue",
  ],
  setupFiles: ["<rootDir>/jest.setup.js"],
};
