import { HTTPResponse } from "@nuxtjs/auth-next";

export interface IAuthService {
  get loggedIn(): boolean;
  get user(): Record<string, unknown> | null;
  logout(...args: unknown[]): Promise<void>;
  setUserToken(token: string): Promise<void | HTTPResponse>;
  setUser(user: unknown): void;
}
