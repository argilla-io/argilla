import { useRunningEnvironment } from "./useRunningEnvironment";

const loadMockedURL = (url: string) => {
  Object.defineProperty(window, "location", {
    value: {
      href: url,
    },
    writable: true,
  });
};

describe("useHuggingFaceHost", () => {
  describe("isRunningOnHuggingFace", () => {
    test("should return true if argilla is running on huggingface", () => {
      loadMockedURL("https://huggingface.co/spaces/damianpumar/awesome-space");

      const { isRunningOnHuggingFace } = useRunningEnvironment();

      expect(isRunningOnHuggingFace()).toBeTruthy();
    });

    test("should return true if argilla is running on huggingface direct url", () => {
      loadMockedURL("https://damianpumar-awesome-space.hf.space/login");

      const { isRunningOnHuggingFace } = useRunningEnvironment();

      expect(isRunningOnHuggingFace()).toBeTruthy();
    });

    test("should return false if argilla is not running on huggingface", () => {
      loadMockedURL("https://damianpumar-awesome-space.otherdomain.com/login");

      const { isRunningOnHuggingFace } = useRunningEnvironment();

      expect(isRunningOnHuggingFace()).toBeFalsy();
    });
  });

  describe("getHuggingFaceInfo", () => {
    test("should return null if argilla is not running on huggingface", () => {
      loadMockedURL("https://damianpumar-awesome-space.otherdomain.com/login");

      const { getHuggingFaceInfo } = useRunningEnvironment();

      expect(getHuggingFaceInfo()).toBeNull();
    });

    test("should return null if argilla is running on huggingface but there is no cookie", () => {
      loadMockedURL("https://huggingface.co/spaces/damianpumar/awesome-space");

      const { getHuggingFaceInfo } = useRunningEnvironment();

      expect(getHuggingFaceInfo()).toBeNull();
    });

    test("should return null if argilla is running on huggingface but cookie is not valid", () => {
      loadMockedURL("https://huggingface.co/spaces/damianpumar/awesome-space");

      Object.defineProperty(document, "cookie", {
        value: "spaces-jwt=invalid-token",
        writable: true,
      });

      const { getHuggingFaceInfo } = useRunningEnvironment();

      expect(getHuggingFaceInfo()).toBeNull();
    });

    test("should return user and space if argilla is running on huggingface and cookie is valid", () => {
      loadMockedURL("https://huggingface.co/spaces/damianpumar/awesome-space");

      Object.defineProperty(document, "cookie", {
        value:
          "spaces-jwt=eyJhbGciOiJFZERTQSJ9.eyJyZWFkIjp0cnVlLCJvbkJlaGFsZk9mIjp7Il9pZCI6IjY0ZWRjNGNhZmRhYjI4YzEwNTkzNjE0YiIsInVzZXIiOiJkYW1pYW5wdW1hciJ9LCJpYXQiOjE3MDY3MTI3MzgsInN1YiI6Ii9zcGFjZXMvY29tbXVuaXR5LWN1cmF0aW9uLWV4cGxvcmVycy9TaGFyZUdQVC1DdXJhdG9ycyIsImV4cCI6MTcwNjc5OTEzOCwiaXNzIjoiaHR0cHM6Ly9odWdnaW5nZmFjZS5jbyJ9.75aY-UQFiDQofXNA62k-9CIhAJlnXXgiUGavPXVUX4jLz0xxzw2KIwPi1719XuCTvVSEIeqtcijTYBCVQIpuDg",
        writable: true,
      });

      const { getHuggingFaceInfo } = useRunningEnvironment();

      expect(getHuggingFaceInfo()).toEqual({
        user: "community-curation-explorers",
        space: "ShareGPT-Curators",
      });
    });
  });
});
