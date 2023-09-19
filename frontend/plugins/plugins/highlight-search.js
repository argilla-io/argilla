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
    const regExp = createFindWordsRegex(sortedKeywords);
    return replaceText(regExp, text);
  };

  const keywordsSpans = function (text, keywords = []) {
    return keywords.flatMap((keyword) => {
      const regex = createFindWordsPattern(keyword);
      return [...text.matchAll(regex)].map((match) => {
        return {
          start: match.index,
          end: match.index + match[0].length,
        };
      });
    });
  };

  const sortByLength = (keywords) => {
    return keywords.sort((a, b) => b.length - a.length);
  };

  function createFindWordsPattern(value) {
    const pattern = "[^A-Za-zÀ-ÿ\u00f1\u00d10-9_@./#&+-]";
    return new RegExp(`(${pattern})${escapeRegExp(value)}(${pattern})`, "gmi");
  }

  const escapeRegExp = function (text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, "\\$&");
  };

  const createFindWordsRegex = (keyWords) => {
    const wordsEscaped = keyWords.map((keyword) => escapeRegExp(keyword));

    const words = wordsEscaped.join("|");

    return new RegExp(`${words}`, "gmi");
  };

  const replaceText = (regex, text) => {
    return htmlText(text).replace(regex, (matched) =>
      matched ? htmlHighlightText(matched) : matched
    );
  };

  const htmlHighlightText = (text) => {
    return `<span class="highlight-text">${htmlText(text)}</span>`;
  };

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
