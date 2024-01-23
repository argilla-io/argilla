import { useFetch, useRoute } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { ProviderType } from "~/v1/domain/entities/oauth/OAuthProvider";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";
import { useRoutes } from "~/v1/infrastructure/services";

export const useOAuthViewModel = () => {
  const routes = useRoute();
  const router = useRoutes();
  const oauthLoginUseCase = useResolve(OAuthLoginUseCase);

  useFetch(async () => {
    await tryLogin();
  });

  const tryLogin = async () => {
    const { params, query } = routes.value;

    const provider = params.provider as ProviderType;

    await oauthLoginUseCase.login(provider, query);

    router.go("/");
  };
};
