import { type NuxtAxiosInstance } from "@nuxtjs/axios";
import { Context } from "@nuxt/types";
import { loadCache } from "../repositories";
import { loadErrorHandler } from "../repositories/AxiosErrorHandler";

type PublicAxiosConfig = {
  enableErrors: boolean;
};

export interface PublicNuxtAxiosInstance extends NuxtAxiosInstance {
  makePublic: (config?: PublicAxiosConfig) => NuxtAxiosInstance;
}

export const useAxiosExtension = (context: Context) => {
  const makePublic = (config: PublicAxiosConfig) => {
    const $axios = context.$axios.create({
      withCredentials: false,
    });

    if (config.enableErrors) {
      loadErrorHandler({
        ...context,
        $axios,
      });
    }

    loadCache($axios);

    return $axios;
  };

  const create = () => {
    return {
      ...context.$axios,
      makePublic: (
        config: PublicAxiosConfig = {
          enableErrors: true,
        }
      ) => makePublic(config),
    } as PublicNuxtAxiosInstance;
  };

  return create;
};
