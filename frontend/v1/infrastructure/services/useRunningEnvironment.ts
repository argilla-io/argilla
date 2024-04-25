import { useResolve } from "ts-injecty";
import { GetEnvironmentUseCase } from "~/v1/domain/usecases/get-environment-use-case";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";

const HUGGING_FACE_EMBEBED_URL = "huggingface.co";
const HUGGING_FACE_DIRECT_URL = ".hf.space";

export const useRunningEnvironment = () => {
  const url = new URL(window.location.href);

  const isEmbebed = () => {
    return window.self !== window.top;
  };

  const isRunningOnHuggingFace = (): boolean => {
    return (
      url.host === HUGGING_FACE_EMBEBED_URL ||
      url.host.endsWith(HUGGING_FACE_DIRECT_URL)
    );
  };

  const getHuggingFaceSpace = async () => {
    const environmentUseCase = useResolve(GetEnvironmentUseCase);
    const environment = await environmentUseCase.execute();

    return environment.huggingFaceSpace;
  };

  const hasHuggingFaceOAuthConfigured = async (): Promise<boolean> => {
    const oauthUseCase = useResolve(OAuthLoginUseCase);

    const providers = await oauthUseCase.getProviders();

    return providers.some((p) => p.isHuggingFace);
  };

  return {
    isEmbebed,
    isRunningOnHuggingFace,
    getHuggingFaceSpace,
    hasHuggingFaceOAuthConfigured,
  };
};
