import { mock } from "@codescouts/test/jest";
import { IOAuthRepository } from "../services/IOAuthRepository";
import { IAuthService } from "../services/IAuthService";
import { OAuthLoginUseCase } from "./oauth-login-use-case";

describe("OAuthLoginUseCase should", () => {
  test("logout user before call the login on backend", async () => {
    const oauthRepository = mock<IOAuthRepository>();
    const auth = mock<IAuthService>();

    oauthRepository.login.mockRejectedValue(new Error("FAKE"));

    const useCase = new OAuthLoginUseCase(oauthRepository, auth);

    try {
      await useCase.login("huggingface", null);
    } catch {
      expect(auth.logout).toHaveBeenCalledTimes(1);
    }
  });

  test("call the backend after logout", async () => {
    const oauthRepository = mock<IOAuthRepository>();
    const auth = mock<IAuthService>();

    const useCase = new OAuthLoginUseCase(oauthRepository, auth);

    await useCase.login("huggingface", null);

    expect(oauthRepository.login).toHaveBeenCalledWith("huggingface", null);
  });

  test("save token if the token is defined", async () => {
    const oauthRepository = mock<IOAuthRepository>();
    const auth = mock<IAuthService>();

    oauthRepository.login.mockResolvedValue("FAKE_TOKEN");

    const useCase = new OAuthLoginUseCase(oauthRepository, auth);

    await useCase.login("huggingface", null);

    expect(auth.setUserToken).toHaveBeenCalledWith("FAKE_TOKEN");
  });

  test("no save token if the token is not defined", async () => {
    const oauthRepository = mock<IOAuthRepository>();
    const auth = mock<IAuthService>();

    oauthRepository.login.mockResolvedValue("");

    const useCase = new OAuthLoginUseCase(oauthRepository, auth);

    await useCase.login("huggingface", null);

    expect(auth.setUserToken).toHaveBeenCalledTimes(0);
  });
});
