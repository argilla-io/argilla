export interface IUserRepository {
  getUser(): Promise<unknown>;
}
