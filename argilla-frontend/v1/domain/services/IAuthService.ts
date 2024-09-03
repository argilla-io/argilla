import { HTTPResponse } from "@nuxtjs/auth-next";

export interface IAuthService {
  logout(...args: unknown[]): Promise<void>;

  setUserToken(token: string): Promise<void | HTTPResponse>;
}
