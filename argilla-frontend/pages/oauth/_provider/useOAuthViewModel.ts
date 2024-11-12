import { useFetch, useRoute } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { ProviderType } from "~/v1/domain/entities/oauth/OAuthProvider";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";
import {
  useRoutes,
  useTranslate,
  useLocalStorage,
} from "~/v1/infrastructure/services";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";

export const useOAuthViewModel = () => {
  const { t } = useTranslate();
  const notification = useNotifications();
  const routes = useRoute();
  const router = useRoutes();
  const oauthLoginUseCase = useResolve(OAuthLoginUseCase);
  const { pop } = useLocalStorage();

  useFetch(async () => {
    await tryLogin();
  });

  const redirect = () => {
    const redirect = pop("redirectTo");
    router.go(redirect || "/");
  };

  const tryLogin = async () => {
    const { params, query } = routes.value;

    const provider = params.provider as ProviderType;

    try {
      await oauthLoginUseCase.login(provider, query);
      redirect();
    } catch {
      notification.notify({
        message: t("argilla.api.errors::UnauthorizedError"),
        type: "danger",
      });
      router.go("/");
    }
  };
};
