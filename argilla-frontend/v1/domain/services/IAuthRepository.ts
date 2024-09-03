export interface IAuthRepository {
  login(username: string, password: string): Promise<string>;
}
