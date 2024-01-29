interface HFSpace {
  space: string;
  user: string;
}

const HUGGING_FACE_EMBEBED_URL = "huggingface.co";

const HUGGING_FACE_DIRECT_URL = ".hf.space";

export const useHuggingFaceHost = () => {
  const url = new URL(window.location.href);

  const isRunningOnHuggingFace = (): HFSpace | undefined => {
    if (url.host === HUGGING_FACE_EMBEBED_URL) {
      const splittedPath = url.pathname
        .replace("/spaces", "")
        .split("/")
        .filter(Boolean);

      const user = splittedPath[0];
      const space = splittedPath[1];

      if (splittedPath.length === 2 && user && space)
        return {
          space,
          user,
        };
    }

    if (url.host.endsWith(HUGGING_FACE_DIRECT_URL)) {
      const splittedPath = url.host
        .replaceAll(HUGGING_FACE_DIRECT_URL, "")
        .split(/-(.*)/s)
        .filter(Boolean);

      const user = splittedPath[0];
      const space = splittedPath[1];

      if (splittedPath.length === 2 && user && space)
        return {
          space,
          user,
        };
    }
  };

  return {
    isRunningOnHuggingFace,
  };
};
