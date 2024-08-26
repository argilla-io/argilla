import { type NuxtAxiosInstance } from "@nuxtjs/axios";

export interface PublicNuxtAxiosInstance extends NuxtAxiosInstance {
  makePublic: () => NuxtAxiosInstance;
}

export const useAxiosExtension = (axiosInstanceFn: () => NuxtAxiosInstance) => {
  const makePublic = (axios: NuxtAxiosInstance) => {
    const publicAxios = axios.create({
      withCredentials: false,
    });

    publicAxios.interceptors.response = axios.interceptors.response;

    return publicAxios;
  };

  const create = () => {
    const axios = axiosInstanceFn();

    return {
      ...axios,
      makePublic: () => makePublic(axios),
    } as PublicNuxtAxiosInstance;
  };

  return create;
};
