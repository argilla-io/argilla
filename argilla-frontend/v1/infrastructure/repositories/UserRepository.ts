import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { IUserRepository } from "~/v1/domain/services/IUserRepository";

const USER_API_ERRORS = {
  ERROR_FETCHING_USER: "ERROR_FETCHING_USER",
};

export class UserRepository implements IUserRepository {
  constructor(private readonly axios: NuxtAxiosInstance) {}

  async getUser() {
    try {
      const url = "/v1/me";

      const { data } = await this.axios.get<unknown>(url);

      return data;
    } catch (error) {
      throw {
        response: USER_API_ERRORS.ERROR_FETCHING_USER,
      };
    }
  }
}
