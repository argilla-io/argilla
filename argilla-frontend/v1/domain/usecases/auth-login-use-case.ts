import { IAuthRepository } from "../services/IAuthRepository";
import { IAuthService } from "../services/IAuthService";
import { LoadUserUseCase } from "./load-user-use-case";

export class AuthLoginUseCase {
  constructor(
    private readonly auth: IAuthService,
    private readonly authRepository: IAuthRepository,
    private readonly loadUser: LoadUserUseCase
  ) {}

  async login(username: string, password: string) {
    await this.auth.logout();

    const token = await this.authRepository.login(username, password);

    if (token) {
      await this.auth.setUserToken(token);

      await this.loadUser.execute();
    }
  }
}
