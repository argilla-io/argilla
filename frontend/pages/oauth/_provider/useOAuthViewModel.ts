import { useFetch, useRoute } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { Notification } from "~/models/Notifications";
import { ProviderType } from "~/v1/domain/entities/oauth/OAuthProvider";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";
import { useRoutes, useTranslate } from "~/v1/infrastructure/services";

export const useOAuthViewModel = () => {
  const t = useTranslate();
  const routes = useRoute();
  const router = useRoutes();
  const oauthLoginUseCase = useResolve(OAuthLoginUseCase);

  useFetch(async () => {
    await tryLogin();
  });

  const tryLogin = async () => {
    const { params, query } = routes.value;

    const provider = params.provider as ProviderType;

    try {
      await oauthLoginUseCase.login(provider, query);
    } catch {
      Notification.dispatch("notify", {
        message: t("argilla.api.errors::UnauthorizedError"),
        type: "error",
      });
    } finally {
      router.go("/");
    }
  };
};
