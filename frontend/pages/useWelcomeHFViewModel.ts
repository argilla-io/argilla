import { useResolve } from "ts-injecty";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";
import { useHuggingFaceHost } from "~/v1/infrastructure/services/useHuggingFaceHost";

export const useWelcomeHFViewModel = () => {
  const oauthLogin = useResolve(OAuthLoginUseCase);
  const { isRunningOnHuggingFace, hasHuggingFaceOAuthConfigured } =
    useHuggingFaceHost();

  const authorize = () => {
    oauthLogin.authorize("huggingface");
  };

  return {
    authorize,
    isRunningOnHuggingFace,
    hasHuggingFaceOAuthConfigured,
  };
};
