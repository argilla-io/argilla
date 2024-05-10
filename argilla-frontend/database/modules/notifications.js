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
const getters = {};

const actions = {
  notify(
    _,
    { message, type, numberOfChars, permanent, buttonText, onClick, onClose }
  ) {
    actions.clear();

    return setTimeout(() => {
      Vue.$toast.open({
        message,
        permanent,
        numberOfChars,
        buttonText,
        onClick() {
          actions.clear();

          if (onClick) onClick();
        },
        onClose() {
          actions.clear();

          if (onClose) onClose();
        },
        type: type || "default",
      });
    }, 100);
  },
  clear() {
    return Vue.$toast.clear();
  },
};

export default {
  getters,
  actions,
};
