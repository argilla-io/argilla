import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { IAuthRepository } from "~/v1/domain/services/IAuthRepository";

export class AuthRepository implements IAuthRepository {
  private readonly axios: NuxtAxiosInstance;
  constructor(axios: NuxtAxiosInstance) {
    this.axios = axios.create({
      withCredentials: false,
    });
  }

  async login(username: string, password: string) {
    const url = "/v1/token";

    const request = this.encodedLoginData(username, password);

    const { data } = await this.axios.post<{ access_token: string }>(
      url,
      request,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      }
    );

    return data.access_token;
  }

  private encodedLoginData(username: string, password: string) {
    return `username=${encodeURIComponent(
      username
    )}&password=${encodeURIComponent(password)}`;
  }
}
