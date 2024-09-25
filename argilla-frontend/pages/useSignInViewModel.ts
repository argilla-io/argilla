import { useResolve } from "ts-injecty";
import { AuthLoginUseCase } from "~/v1/domain/usecases/auth-login-use-case";

export const useSignInViewModel = () => {
  const useCase = useResolve(AuthLoginUseCase);

  const login = async (username: string, password: string) => {
    await useCase.login(username, password);
  };

  return {
    login,
  };
};
