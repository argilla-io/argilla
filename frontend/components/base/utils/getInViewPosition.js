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

const margin = 0;

const isAboveOfViewport = (element, position) =>
  position.top <= margin - parseInt(getComputedStyle(element).marginTop, 10);

const isBelowOfViewport = (element, position) =>
  position.top + element.offsetHeight + margin >=
  window.innerHeight - parseInt(getComputedStyle(element).marginTop, 10);

const isOnTheLeftOfViewport = (element, position) =>
  position.left <= margin - parseInt(getComputedStyle(element).marginLeft, 10);

const isOnTheRightOfViewport = (element, position) =>
  position.left + element.offsetWidth + margin >=
  window.innerWidth - parseInt(getComputedStyle(element).marginLeft, 10);

const getInViewPosition = (element, position) => {
  const computedStyle = getComputedStyle(element);

  if (isAboveOfViewport(element, position)) {
    position.top = margin - parseInt(computedStyle.marginTop, 10);
  }

  if (isOnTheLeftOfViewport(element, position)) {
    position.left = margin - parseInt(computedStyle.marginLeft, 10);
  }

  if (isOnTheRightOfViewport(element, position)) {
    position.left =
      window.innerWidth -
      margin -
      element.offsetWidth -
      parseInt(computedStyle.marginLeft, 10);
  }

  if (isBelowOfViewport(element, position)) {
    position.top =
      window.innerHeight -
      margin -
      element.offsetHeight -
      parseInt(computedStyle.marginTop, 10);
  }

  return position;
};

export default getInViewPosition;
