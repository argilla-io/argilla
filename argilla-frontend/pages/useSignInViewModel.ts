import { useResolve } from "ts-injecty";
import { AuthLoginUseCase } from "~/v1/domain/usecases/auth-login-use-case";
import { useRoutes, useLocalStorage } from "~/v1/infrastructure/services";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";

export const useSignInViewModel = () => {
  const useCase = useResolve(AuthLoginUseCase);
  const router = useRoutes();
  const notification = useNotifications();
  const { pop } = useLocalStorage();

  const redirect = () => {
    const redirect = pop<string | null>("redirectTo");
    router.go(redirect || "/");
  };

  const login = async (username: string, password: string) => {
    await useCase.login(username, password);
    notification.clear();
    redirect();
  };

  return {
    login,
  };
};
