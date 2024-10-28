import { mock } from "@codescouts/test/jest";
import { IOAuthRepository } from "../services/IOAuthRepository";
import { IAuthService } from "../services/IAuthService";
import { RouterService } from "../services/RouterService";
import { IUserRepository } from "../services/IUserRepository";
import { OAuthLoginUseCase } from "./oauth-login-use-case";
import { LoadUserUseCase } from "./load-user-use-case";

describe("OAuthLoginUseCase should", () => {
  test("logout user before call the login on backend", async () => {
    const auth = mock<IAuthService>();
    const router = mock<RouterService>();
    const oauthRepository = mock<IOAuthRepository>();
    const loadUserUseCase = new LoadUserUseCase(auth, mock<IUserRepository>());

    oauthRepository.login.mockRejectedValue(new Error("FAKE"));

    const useCase = new OAuthLoginUseCase(
      auth,
      oauthRepository,
      loadUserUseCase,
      router
    );

    try {
      await useCase.login("huggingface", null);
    } catch {
      expect(auth.logout).toHaveBeenCalledTimes(1);
    }
  });

  test("call the backend after logout", async () => {
    const auth = mock<IAuthService>();
    const router = mock<RouterService>();

    const oauthRepository = mock<IOAuthRepository>();
    const loadUserUseCase = new LoadUserUseCase(auth, mock<IUserRepository>());

    const useCase = new OAuthLoginUseCase(
      auth,
      oauthRepository,
      loadUserUseCase,
      router
    );

    await useCase.login("huggingface", null);

    expect(oauthRepository.login).toHaveBeenCalledWith("huggingface", null);
  });

  test("save token if the token is defined", async () => {
    const auth = mock<IAuthService>();
    const router = mock<RouterService>();
    const oauthRepository = mock<IOAuthRepository>();
    const loadUserUseCase = new LoadUserUseCase(auth, mock<IUserRepository>());

    router.getQuery.mockReturnValue({});

    oauthRepository.login.mockResolvedValue("FAKE_TOKEN");

    const useCase = new OAuthLoginUseCase(
      auth,
      oauthRepository,
      loadUserUseCase,
      router
    );

    await useCase.login("huggingface", null);

    expect(auth.setUserToken).toHaveBeenCalledWith("FAKE_TOKEN");
  });

  test("no save token if the token is not defined", async () => {
    const auth = mock<IAuthService>();
    const router = mock<RouterService>();
    const oauthRepository = mock<IOAuthRepository>();
    const loadUserUseCase = new LoadUserUseCase(auth, mock<IUserRepository>());

    oauthRepository.login.mockResolvedValue("");

    const useCase = new OAuthLoginUseCase(
      auth,
      oauthRepository,
      loadUserUseCase,
      router
    );

    await useCase.login("huggingface", null);

    expect(auth.setUserToken).toHaveBeenCalledTimes(0);
  });
});
