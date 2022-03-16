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
  const escapeText = function (text) {
    return text
      .toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  };

  const regexFromTerm = function (term) {
    let q = term.replace(/[-[\]{}()*+?.,\\/^$|#\s]/g, "");
    return new RegExp(q, "gi");
  };

  const highlightSearch = function (query, text) {
    const escapedText = escapeText(text);
    if (!query) {
      return text;
    }

    return escapedText
      .toString()
      .replace(
        regexFromTerm(query),
        (match) => `<span class="highlight-text">${match}</span>`
      );
  };

  const highlightKeywords = function (text, keywords) {
    let escapedText = escapeText(text).toString();

    (keywords || []).forEach((keyword) => {
      escapedText = escapedText.replace(
        regexFromTerm(keyword),
        (match) => `<span class="highlight-text">${match}</span>`
      );
    });

    return escapedText;
  };

  inject("highlightSearch", highlightSearch);
  inject("highlightKeywords", highlightKeywords);
};
