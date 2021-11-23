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
import { getCurrentWorkspace } from "@/models/User";
export default ({ $axios, app }) => {
  Model.setAxios($axios);

  $axios.interceptors.request.use(async (config) => {
    const currentUser = app.$auth.user;

    if (!currentUser) {
      return config;
    }

    const currentWorkspace = await getCurrentWorkspace(app.$auth);

    if (currentWorkspace && currentUser.username !== currentWorkspace) {
      var wsQueryParam = "workspace=" + currentWorkspace;
      if (config.url.includes("?")) {
        wsQueryParam = "&" + wsQueryParam;
      } else wsQueryParam = "?" + wsQueryParam;

      config.url += wsQueryParam;
    }

    return config;
  });

  $axios.onError((error) => {
    const code = parseInt(error.response && error.response.status);
    if (error instanceof ExpiredAuthSessionError || [401, 403].includes(code)) {
      app.$auth.logout();
    }

    switch (code) {
      case 400:
      case 422:
        (error.response.data.detail || [undefined]).forEach(({ msg }) => {
          Notification.dispatch("notify", {
            message: "Error: " + (msg || "Unknown"),
            type: "error",
          });
        });
        break;
      case 404:
        Notification.dispatch("notify", {
          message: "Warning: " + error.response.data.detail,
          type: "warning",
        });
        break;
      default:
        Notification.dispatch("notify", {
          message: error,
          type: "error",
        });
    }

    throw error;
  });
};
