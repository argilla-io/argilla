export interface IAuthService {
  logout(...args: unknown[]): Promise<void>;

  setUserToken(token: string);
}
