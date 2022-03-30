<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->

<template>
  <div class="record">
    <div class="content">
      <record-token-classification-annotation
        :dataset="dataset"
        :record="record"
        :visualTokens="visualTokens"
        v-if="annotationEnabled"
      />
      <record-token-classification-exploration
        :dataset="dataset"
        :record="record"
        :visualTokens="visualTokens"
        v-else
      />
    </div>
  </div>
</template>

<script>
import { indexOf, length } from "stringz";

export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    visualTokens() {
      // This is used for both, annotation ad exploration components
      const recordHasEmoji = this.record.text.containsEmoji;
      const searchKeywordsSpans = this.$keywordsSpans(
        this.record.text,
        this.record.search_keywords
      );

      const { visualTokens } = this.record.tokens.reduce(
        ({ visualTokens, startPosition }, token, index) => {
          const start = recordHasEmoji
            ? indexOf(this.record.text, token, startPosition)
            : this.record.text.indexOf(token, startPosition);
          const nextStart = recordHasEmoji
            ? indexOf(
                this.record.text,
                this.record.tokens[index + 1],
                startPosition
              )
            : this.record.text.indexOf(
                this.record.tokens[index + 1],
                startPosition
              );
          const end = start + (recordHasEmoji ? length(token) : token.length);
          const charsBetweenTokens = this.record.text.slice(end, nextStart);

          let highlighted = false;
          for (let highlight of searchKeywordsSpans) {
            if (highlight.start <= start && highlight.end >= end) {
              highlighted = true;
              break;
            }
          }
          return {
            visualTokens: [
              ...visualTokens,
              { start, end, highlighted, text: token, charsBetweenTokens },
            ],
            startPosition: end,
          };
        },
        {
          visualTokens: [],
          startPosition: 0,
        }
      );
      return visualTokens;
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  padding: 56px 20px 50px 50px;
  display: block;
  margin-bottom: 0;
  @include font-size(18px);
  line-height: 34px;
  .list__item--annotation-mode & {
    padding-left: 65px;
  }
}
.content {
  position: relative;
  white-space: pre-line;
  &__input {
    padding-right: 200px;
  }
  &__actions-buttons {
    margin-right: 0;
    margin-left: auto;
    display: flex;
    min-width: 20%;
    .re-button {
      min-height: 32px;
      line-height: 32px;
      display: block;
      margin: 1.5em auto 0 0;
      & + .re-button {
        margin-left: 1em;
      }
    }
  }
}
</style>
