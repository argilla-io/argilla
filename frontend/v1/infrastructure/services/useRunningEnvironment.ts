import { useResolve } from "ts-injecty";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";

interface HFSpace {
  space: string;
  user: string;
}

const HUGGING_FACE_EMBEBED_URL = "huggingface.co";
const HUGGING_FACE_DIRECT_URL = ".hf.space";

export const useRunningEnvironment = () => {
  const url = new URL(window.location.href);

  const parseHuggingFaceData = (data: string[]) => {
    const user = data[0];
    const space = data[1];

    if (data.length === 2 && user && space)
      return {
        space,
        user,
      };

    return undefined;
  };

  const isEmbebed = () => {
    return window.self !== window.top;
  };

  const isRunningOnHuggingFace = (): HFSpace | undefined => {
    if (url.host === HUGGING_FACE_EMBEBED_URL) {
      const paramsData = url.pathname
        .replace("/spaces", "")
        .split("/")
        .filter(Boolean);

      return parseHuggingFaceData(paramsData);
    }

    if (url.host.endsWith(HUGGING_FACE_DIRECT_URL)) {
      const paramsData = url.host
        .replaceAll(HUGGING_FACE_DIRECT_URL, "")
        .split(/-(.*)/s)
        .filter(Boolean);

      return parseHuggingFaceData(paramsData);
    }
  };

  const hasHuggingFaceOAuthConfigured = async (): Promise<boolean> => {
    const oauthUseCase = useResolve(OAuthLoginUseCase);

    const providers = await oauthUseCase.getProviders();

    return providers.some((p) => p.isHuggingFace);
  };

  return {
    isEmbebed,
    isRunningOnHuggingFace,
    hasHuggingFaceOAuthConfigured,
  };
};
