import { useResolve } from "ts-injecty";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";

interface HFSpace {
  space: string;
  user: string;
}

const HUGGING_FACE_DIRECT_URL = ".hf.space";

export const useRunningEnvironment = () => {
  const url = new URL(window.location.href);

  const isEmbebed = () => {
    return window.self !== window.top;
  };

  const isRunningOnHuggingFace = (): HFSpace | undefined => {
    if (url.host.endsWith(HUGGING_FACE_DIRECT_URL)) {
      const paramsData = url.host
        .replaceAll(HUGGING_FACE_DIRECT_URL, "")
        .split(/-(.*)/s)
        .filter(Boolean);

      const user = paramsData[0];
      const space = paramsData[1];

      if (paramsData.length === 2 && user && space) {
        return {
          space,
          user,
        };
      }
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
