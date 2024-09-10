import { PublicNuxtAxiosInstance } from "../services/useAxiosExtension";
import { IUserRepository } from "~/v1/domain/services/IUserRepository";

export class UserRepository implements IUserRepository {
  constructor(private readonly axios: PublicNuxtAxiosInstance) {}

  async getUser() {
    const url = "/v1/me";

    const { data } = await this.axios.get<unknown>(url);

    return data;
  }
}
