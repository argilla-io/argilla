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
  test("should return true and user name if argilla is running on huggingface", () => {
    loadMockedURL("https://huggingface.co/spaces/damianpumar/awesome-space");

    const { isRunningOnHuggingFace } = useRunningEnvironment();

    expect(isRunningOnHuggingFace()).toBeTruthy();
  });

  test("should be false if argilla is not running on huggingface", () => {
    loadMockedURL("https://other.domain.com/damianpumar/awesome-space");

    const { isRunningOnHuggingFace } = useRunningEnvironment();

    expect(isRunningOnHuggingFace()).toBeFalsy();
  });
});
