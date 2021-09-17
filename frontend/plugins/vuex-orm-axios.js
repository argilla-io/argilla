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

export default ({ $axios, app }) => {
  Model.setAxios($axios);

  $axios.onError((error) => {
    const code = parseInt(error.response && error.response.status);
    if (error instanceof ExpiredAuthSessionError || [401, 403].includes(code)) {
      app.$auth.logout();
    }

    if (code === 400) {
      // Add more erros once are better handled
      return Notification.dispatch("notify", {
        message:
          "Error: " + JSON.stringify(error.response.data.detail || error),
        type: "error",
      });
    }

    return Notification.dispatch("notify", {
      message: error,
      type: "error",
    });
  });
};
