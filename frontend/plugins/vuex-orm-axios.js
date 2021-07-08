import { Model } from "@vuex-orm/core";
import { Notification } from "@/models/Notifications";

export default ({ $axios }) => {
  Model.setAxios($axios);

  $axios.onError((error) => {
    return Notification.dispatch("notify", {
      message: error,
      type: "error",
    });
  });
};
