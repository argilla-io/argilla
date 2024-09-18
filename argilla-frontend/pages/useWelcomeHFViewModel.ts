import { useResolve } from "ts-injecty";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";
import { useRunningEnvironment } from "~/v1/infrastructure/services/useRunningEnvironment";

export const useWelcomeHFViewModel = () => {
  const oauthLogin = useResolve(OAuthLoginUseCase);
  const { hasHuggingFaceOAuthConfigured, getHuggingFaceSpace } =
    useRunningEnvironment();

  const authorize = () => {
    oauthLogin.authorize("huggingface");
  };

  return {
    authorize,
    hasHuggingFaceOAuthConfigured,
    getHuggingFaceSpace,
  };
};
