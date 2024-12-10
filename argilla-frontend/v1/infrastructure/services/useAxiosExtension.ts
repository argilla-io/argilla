import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { loadCache } from "../repositories";
import { loadErrorHandler } from "../repositories/AxiosErrorHandler";
import { useTranslate } from "./useTranslate";

type PublicAxiosConfig = {
  enableErrors: boolean;
};

export interface PublicNuxtAxiosInstance extends NuxtAxiosInstance {
  makePublic: (config?: PublicAxiosConfig) => NuxtAxiosInstance;
}

export const useAxiosExtension = (axiosInstanceFn: () => NuxtAxiosInstance) => {
  const makePublic = (axios: NuxtAxiosInstance, config: PublicAxiosConfig) => {
    const { t } = useTranslate();

    const publicAxios = axios.create({
      withCredentials: false,
    });

    if (config.enableErrors) {
      loadErrorHandler(publicAxios, t);
    }

    loadCache(publicAxios);

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
