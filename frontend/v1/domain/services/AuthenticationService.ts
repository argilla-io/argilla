export interface AuthenticationService {
  setUserToken(token: string): Promise<unknown>;
}
