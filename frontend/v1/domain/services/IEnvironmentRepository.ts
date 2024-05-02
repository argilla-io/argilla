import { Environment } from "../entities/environment/Environment";

export interface IEnvironmentRepository {
  getEnvironment(): Promise<Environment>;
}
