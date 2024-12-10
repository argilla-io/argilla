import { AxiosError } from "axios";
import { useNotifications } from "../services";

type BackendError = {
  detail:
    | {
        params: {
          detail: string;
        };
      }
    | string;
  code?: string;
  message?: string;
};

export const loadErrorHandler = (axios, t: (key: string) => string) => {
  const notification = useNotifications();

  axios.onError((error: AxiosError<BackendError>) => {
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
