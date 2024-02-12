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

import { Model } from "@vuex-orm/core";
import { ExpiredAuthSessionError } from "@nuxtjs/auth-next/dist/runtime";
import { AxiosError } from "axios";
import { Notification } from "@/models/Notifications";

import { currentWorkspace } from "@/models/Workspace";

type BackendError = {
  detail: {
    params: {
      detail: string;
    };
  };
};

export default ({ $axios, app }) => {
  Model.setAxios($axios);

  $axios.interceptors.request.use((config) => {
    const currentUser = app.$auth.user;

    if (!currentUser) {
      return config;
    }

    const ws = currentWorkspace(app.context.route);
    if (ws) {
      config.headers["X-Argilla-Workspace"] = ws;
    }
    return config;
  });

  $axios.onError((error: AxiosError<BackendError>) => {
    const { data, status } = error.response ?? {};
    const t = (key: string) => app.i18n.t(key);

    Notification.dispatch("clear");

    switch (status) {
      case 404:
        Notification.dispatch("notify", {
          message: `${t("validations.type.warning")}: ${
            data.detail.params.detail
          }`,
          type: "warning",
        });
        break;
      case 401: {
        Notification.dispatch("notify", {
          message: t("validations.unauthorized"),
          type: "error",
        });

        if (error instanceof ExpiredAuthSessionError) app.$auth.logout();

        break;
      }
    }

    throw error;
  });
};
