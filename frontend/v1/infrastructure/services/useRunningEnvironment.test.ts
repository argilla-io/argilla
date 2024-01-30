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
  test("should return space and user name if argilla is running on huggingface", () => {
    loadMockedURL("https://huggingface.co/spaces/damianpumar/awesome-space");

    const { isRunningOnHuggingFace } = useRunningEnvironment();

    expect(isRunningOnHuggingFace()).toEqual({
      space: "awesome-space",
      user: "damianpumar",
    });
  });

  test("should return space and username if argilla is running on huggingface direct url", () => {
    loadMockedURL("https://damianpumar-awesome-space.hf.space/login");

    const { isRunningOnHuggingFace } = useRunningEnvironment();

    expect(isRunningOnHuggingFace()).toEqual({
      space: "awesome-space",
      user: "damianpumar",
    });
  });

  test("should be undefined if argilla is not running on huggingface", () => {
    loadMockedURL("https://other.domain.com/damianpumar/awesome-space");

    const { isRunningOnHuggingFace } = useRunningEnvironment();

    expect(isRunningOnHuggingFace()).toBeUndefined();
  });
});
