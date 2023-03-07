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
  const highlightKeywords = function (text, keywords) {
    const sortedKeywords = sortByLength([...keywords]);
    const pattern = sortedKeywords.map((keyword) => createPattern(keyword));
    const regExp = createRegExp(pattern.join("|"));
    return replaceText(regExp, text);
  };

  const keywordsSpans = function (text, keywords) {
    return (keywords || []).flatMap((keyword) => {
      const regex = createRegExp(createPattern(keyword));
      return [...text.matchAll(regex)].map((match) => {
        return {
          start: match.index,
          end: match.index + match[0].length,
        };
      });
    });
  };

  function sortByLength(keywords) {
    return (keywords || []).sort((a, b) => b.length - a.length);
  }

  function createPattern(value) {
    const pattern = "[^A-Za-z0-9_@./#&+-]";
    return `(${pattern})${escapeRegExp(value)}(${pattern})`;
  }

  const escapeRegExp = function (text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
  };

  function createRegExp(pattern) {
    return new RegExp(pattern, "gmi");
  }

  function replaceText(regex, text) {
    return htmlText(text).replace(regex, (matched) =>
      matched ? htmlHighlightText(matched) : matched
    );
  }

  function htmlHighlightText(text) {
    return `<span class="highlight-text">${htmlText(text)}</span>`;
  }

  const htmlText = function (text) {
    return text
      .toString()
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  };

  inject("highlightKeywords", highlightKeywords);
  inject("keywordsSpans", keywordsSpans);
  inject("htmlText", htmlText);
  inject("htmlHighlightText", htmlHighlightText);
};
