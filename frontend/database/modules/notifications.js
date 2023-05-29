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
  notify(_, { message, type, numberOfChars, buttonText, onClick, onClose }) {
    return Vue.$toast.open({
      message,
      numberOfChars,
      buttonText,
      onClick,
      onClose,
      type: type || "default",
    });
  },
  clear() {
    return Vue.$toast.clear();
  },
};

export default {
  getters,
  actions,
};
