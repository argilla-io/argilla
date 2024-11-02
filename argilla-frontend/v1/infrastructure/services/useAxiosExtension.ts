import { type NuxtAxiosInstance } from "@nuxtjs/axios";

type PublicAxiosConfig = {
  enableErrors: boolean;
};

export interface PublicNuxtAxiosInstance extends NuxtAxiosInstance {
  makePublic: (config?: PublicAxiosConfig) => NuxtAxiosInstance;
}

export const useAxiosExtension = (axiosInstanceFn: () => NuxtAxiosInstance) => {
  const makePublic = (axios: NuxtAxiosInstance, config: PublicAxiosConfig) => {
    const publicAxios = axios.create({
      withCredentials: false,
    });

    if (config.enableErrors) {
      publicAxios.interceptors.response = axios.interceptors.response;
    }

    return publicAxios;
  };

  const create = () => {
    const axios = axiosInstanceFn();

    return {
      ...axios,
      makePublic: (
        config: PublicAxiosConfig = {
          enableErrors: true,
        }
      ) => makePublic(axios, config),
    } as PublicNuxtAxiosInstance;
  };

  return create;
};
