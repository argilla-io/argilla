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
import { Notification } from "@/models/Notifications";

import { currentWorkspace } from "@/models/Workspace";

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

  $axios.onError((error) => {
    const code = parseInt(error.response && error.response.status);
    if (error instanceof ExpiredAuthSessionError || code === 401) {
      app.$auth.logout();
    }

    const detail = error.response.data.detail || {
      code: undefined,
      params: {},
    };

    Notification.dispatch("clear");

    switch (code) {
      case 400:
        Notification.dispatch("notify", {
          message: Object.entries(detail.params)
            .map(([k, v]) => `Error ${k}: ${v}`)
            .join("\n"),
          type: "error",
        });
        break;
      case 422: {
        if (typeof detail === "string") {
          Notification.dispatch("notify", {
            message: `Error: ${detail}`,
            type: "error",
          });
        } else {
          (detail.params.errors || [undefined]).forEach(({ msg }) => {
            Notification.dispatch("notify", {
              message: "Error: " + (msg || "Unknown"),
              type: "error",
            });
          });
        }

        break;
      }
      case 404:
        Notification.dispatch("notify", {
          message: `Warning: ${detail.params.detail}`,
          type: "warning",
        });
        break;
      case 401: {
        Notification.dispatch("notify", {
          message: app.i18n.t(detail.code),
          type: "error",
        });
        break;
      }
      default: {
        Notification.dispatch("notify", {
          message: `Error: ${detail.params.details ?? detail.params.message}`,
          type: "error",
        });
      }
    }

    throw error;
  });
};
