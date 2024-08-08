import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { PublicNuxtAxiosInstance } from "../services/useAxiosExtension";
import { IUserRepository } from "~/v1/domain/services/IUserRepository";

export class UserRepository implements IUserRepository {
  private readonly axios: NuxtAxiosInstance;

  constructor(axios: PublicNuxtAxiosInstance) {
    this.axios = axios.makePublic();
  }

  async getUser() {
    const url = "/v1/me";

    const { data } = await this.axios.get<unknown>(url);

    return data;
  }
}
