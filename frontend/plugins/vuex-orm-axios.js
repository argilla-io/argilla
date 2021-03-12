import { Model } from "@vuex-orm/core";
import { ExpiredAuthSessionError } from "@nuxtjs/auth-next/dist/runtime";
import { Notification } from "@/models/Notifications";

export default ({ $axios, app }) => {
  Model.setAxios($axios);

  $axios.onError((error) => {
    const code = parseInt(error.response && error.response.status);
    if (error instanceof ExpiredAuthSessionError || [401, 403].includes(code)) {
      app.$auth.logout();
    }
    return Notification.dispatch("notify", {
      message: error,
      type: "error",
    });
    return Promise.reject(error);
  });
};
