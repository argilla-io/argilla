import { useRoute } from "@nuxtjs/composition-api";
import { useResolve } from "ts-injecty";
import { onMounted } from "vue-demi";
import { ProviderType } from "~/v1/domain/entities/oauth/OAuthProvider";
import { OAuthLoginUseCase } from "~/v1/domain/usecases/oauth-login-use-case";
import { useRoutes } from "~/v1/infrastructure/services";

export const useOAuthViewModel = () => {
  const routes = useRoute();
  const router = useRoutes();
  const oauthLoginUseCase = useResolve(OAuthLoginUseCase);

  onMounted(async () => {
    const provider = routes.value.params.provider as ProviderType;

    const query = Object.keys(routes.value.query)
      .map((key) => `${key}=${routes.value.query[key]}`)
      .join("&");

    if (query) {
      await oauthLoginUseCase.login(provider, query);
    }

    router.go("/");
  });
};
