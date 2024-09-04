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

import Vue from "vue";
import Toast from "./Toast.vue";
import eventBus from "./bus";

export const toast = (globalOptions = {}) => {
  return {
    open(options) {
      let message;
      if (typeof options === "string") message = options;

      const defaultOptions = {
        message,
      };

      const propsData = Object.assign(
        {},
        defaultOptions,
        globalOptions,
        options
      );

      return new (Vue.extend(Toast))({
        el: document.createElement("div"),
        propsData,
      });
    },
    clear() {
      eventBus.$emit("toast.clear");
    },
    success(message, options = {}) {
      return this.open(
        Object.assign(
          {},
          {
            message,
            type: "success",
          },
          options
        )
      );
    },
    danger(message, options = {}) {
      return this.open(
        Object.assign(
          {},
          {
            message,
            type: "danger",
          },
          options
        )
      );
    },
    info(message, options = {}) {
      return this.open(
        Object.assign(
          {},
          {
            message,
            type: "info",
          },
          options
        )
      );
    },
    warning(message, options = {}) {
      return this.open(
        Object.assign(
          {},
          {
            message,
            type: "warning",
          },
          options
        )
      );
    },
    default(message, options = {}) {
      return this.open(
        Object.assign(
          {},
          {
            message,
            type: "default",
          },
          options
        )
      );
    },
  };
};
