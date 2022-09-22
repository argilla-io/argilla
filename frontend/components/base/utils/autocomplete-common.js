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

export default {
  props: {
    debounce: {
      type: Number,
      default: 1e3,
    },
    disabled: Boolean,
    fetch: {
      type: Function,
    },
    filterList: Function,
    list: {
      type: Array,
      default() {
        return [];
      },
    },
    minChars: {
      type: Number,
      default: 1,
    },
    name: String,
    prepareResponseData: Function,
    printAttribute: {
      type: String,
      default: "name",
    },
    queryParam: {
      type: String,
      default: "q",
    },

    maxHeight: {
      type: Number,
      default: 0,
    },

    required: Boolean,

    maxRes: {
      type: Number,
      default: 0,
    },
  },
  methods: {
    onFocus() {
      if (this.parentContainer) {
        this.parentContainer.isFocused = true;
      }
    },
    onBlur() {
      this.parentContainer.isFocused = false;
      this.setParentValue();
    },
    verifyProps() {
      if (!this.parentContainer) {
        return this.throwErrorDestroy(
          "You should wrap the md-input in a md-input-container"
        );
      }
      if (this.listIsEmpty && this.filterList) {
        return this.throwErrorDestroy(
          "You should use a `filterList` function prop with the `list` prop"
        );
      }
      if (!this.fetch && this.listIsEmpty) {
        return this.throwErrorDestroy("You should use a `fetch` function prop");
      }
    },
    throwErrorDestroy(errorMessage) {
      this.$destroy();
      throw new Error(errorMessage);
    },
  },
};
