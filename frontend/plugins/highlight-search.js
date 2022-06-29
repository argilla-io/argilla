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
  const htmlText = function (text) {
    return text
      .toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  };

  function htmlHighlightText(text) {
    return `<span class="highlight-text">${htmlText(text)}</span>`;
  }

  const regexFromTerm = function (term) {
    let q = term.replace(/[-[\]{}()*+?.,\\/^$|#\s]/g, "");
    return new RegExp(q, "gi");
  };

  const escapeRegExp = function (text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
  };

  const highlightSearch = function (query, text) {
    const escapedText = htmlText(text);
    if (!query) {
      return text;
    }

    return escapedText.replace(
      regexFromTerm(query),
      (match) => `<span class="highlight-text">${match}</span>`
    );
  };

  const highlightKeywords = function (text, keywords) {
    const sortedKeywords = ([...keywords] || []).sort(
      (a, b) => b.length - a.length
    );
    text = htmlText(text);
    sortedKeywords.forEach((keyword) => {
      const regex = new RegExp(
        `([^a-zA-ZÀ-ÿ\u00f1\u00d1]|^)${escapeRegExp(keyword)}`,
        "gmi"
      );
      text = text.replace(regex, (match) => htmlHighlightText(match));
    });

    return text;
  };

  const keywordsSpans = function (text, keywords) {
    return (keywords || []).flatMap((keyword) => {
      const regex = new RegExp(
        `([^a-zA-ZÀ-ÿ\u00f1\u00d1]|^)${escapeRegExp(keyword)}`,
        "gmi"
      );
      return [...text.matchAll(regex)].map((match) => {
        return {
          start: match.index,
          end: match.index + match[0].length,
        };
      });
    });
  };

  inject("highlightSearch", highlightSearch);
  inject("highlightKeywords", highlightKeywords);
  inject("keywordsSpans", keywordsSpans);
  inject("htmlText", htmlText);
  inject("htmlHighlightText", htmlHighlightText);
};
