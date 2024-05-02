import { IEnvironmentRepository } from "../services/IEnvironmentRepository";

export class GetEnvironmentUseCase {
  constructor(private readonly environmentRepository: IEnvironmentRepository) {}

  execute() {
    return this.environmentRepository.getEnvironment();
  }
}
