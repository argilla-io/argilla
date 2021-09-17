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

export default (context, inject) => {
  const highlightSearch = function (query, text) {
    const escapedText = text
      .toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
    if (!query) {
      return escapedText;
    }
    let q = query.replace(/[-[\]{}()*+?.,\\/^$|#\s]/g, "");
    return escapedText
      .toString()
      .replace(
        new RegExp(q, "gi"),
        (match) => `<span class="highlight-text">${match}</span>`
      );
  };
  inject("highlightSearch", highlightSearch);
};
