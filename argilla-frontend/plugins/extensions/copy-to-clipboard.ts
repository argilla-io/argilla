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

export default (_, inject) => {
  const unsecuredCopyToClipboard = (text) => {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
      document.execCommand("copy");
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error("Unable to copy to clipboard", err);
    }

    document.body.removeChild(textArea);
  };

  const copyToClipboard = function (text) {
    if (window.isSecureContext && navigator.clipboard) {
      navigator.clipboard.writeText(text);
    } else {
      unsecuredCopyToClipboard(text);
    }
  };

  inject("copyToClipboard", copyToClipboard);
};
