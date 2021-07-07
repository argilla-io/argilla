import { Model } from "@vuex-orm/core";
import { ExpiredAuthSessionError } from "@nuxtjs/auth-next/dist/runtime";
import { Notification } from "@/models/Notifications";

export default ({ $axios }) => {
  Model.setAxios($axios);

  $axios.onError((error) => {
    const code = parseInt(error.response && error.response.status);
    return Notification.dispatch("notify", {
      message: error,
      type: "error",
    });
  });
};
