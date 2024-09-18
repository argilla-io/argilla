process.env.TZ = "UTC";

module.exports = {
  moduleFileExtensions: ["ts", "js", "json", "vue"],
  moduleNameMapper: {
    "assets/(.*)": "<rootDir>/assets/$1",
    "^~/(.*)$": "<rootDir>/$1",
    "^~~/(.*)$": "<rootDir>/$1",
    "^@/(.*)$": "<rootDir>/$1",
  },
  modulePathIgnorePatterns: ["<rootDir>/e2e"],
  transform: {
    "^.+\\.js$": "babel-jest",
    "^.+\\.ts$": "babel-jest",
    ".*\\.(vue)$": "vue-jest",
    "^.+\\.svg$": "jest-transform-stub",
  },
  snapshotSerializers: ["<rootDir>/node_modules/jest-serializer-vue"],
  testEnvironment: "jsdom",
  collectCoverageFrom: [
    "<rootDir>/components/**/*.vue",
    "<rootDir>/pages/*.vue",
  ],
  setupFiles: ["<rootDir>/jest.setup.ts"],
};
