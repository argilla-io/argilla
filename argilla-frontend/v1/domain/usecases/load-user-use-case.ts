import { IAuthService } from "../services/IAuthService";
import { IUserRepository } from "../services/IUserRepository";

export class LoadUserUseCase {
  constructor(
    private readonly auth: IAuthService,
    private readonly userRepository: IUserRepository
  ) {}

  async execute() {
    if (!this.auth.loggedIn) return;
    if (this.auth.user?.id) return;

    const user = await this.userRepository.getUser();

    this.auth.setUser(user);
  }
}
