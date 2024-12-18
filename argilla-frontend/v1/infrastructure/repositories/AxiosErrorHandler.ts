import { Context } from "@nuxt/types";
import { useNotifications } from "../services";

export const loadErrorHandler = (context: Context) => {
  const axios = context.$axios;
  const t = (key: string) => context.app.i18n.t(key).toString();

  const notification = useNotifications();

  axios.onError((error) => {
    const { status, data } = error.response ?? {};

    notification.clear();

    const errorHandledKey = `validations.http.${status}.message`;
    const handledTranslatedError = t(errorHandledKey);

    if (handledTranslatedError !== errorHandledKey) {
      notification.notify({
        message: handledTranslatedError,
        type: "danger",
      });
    }

    if (data.code) {
      const errorHandledKey = `validations.businessLogic.${data.code}.message`;
      const handledTranslatedError = t(errorHandledKey);

      if (handledTranslatedError !== errorHandledKey) {
        notification.notify({
          message: handledTranslatedError,
          type: "danger",
        });
      }
    } else if (data.detail && typeof data.detail === "string") {
      notification.notify({
        message: data.detail.toString(),
        type: "danger",
      });
    }

    throw error;
  });
};
