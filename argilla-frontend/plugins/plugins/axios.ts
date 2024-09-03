/*
 * coding=utf-8
 * Copyright 2021-present, the Recognai S.L. team.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { AxiosError } from "axios";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";

type BackendError = {
  detail: {
    params: {
      detail: string;
    };
  };
  code?: string;
  message?: string;
};

export default ({ $axios, app }) => {
  const notification = useNotifications();

  $axios.onError((error: AxiosError<BackendError>) => {
    const { status, data } = error.response ?? {};
    const t = (key: string) => app.i18n.t(key);

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
    }

    throw error;
  });
};
