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
  <div
    v-if="textSpans.length"
    ref="list"
    class="content__input"
    @mouseup="reset($event)"
    v-click-outside="onReset"
  >
    <TextSpan
      v-for="(token, i) in textSpans"
      :key="i"
      :record="record"
      :token="token"
      :span-id="i"
      :dataset="dataset"
      :suggestedLabel="suggestedLabel"
      :class="[
        isSelected(i, selectionStart, selectionEnd) ||
        isSelected(i, selectionStart, selectionOver)
          ? 'selected'
          : '',
        isLastSelected(i, selectionEnd) ? 'last-selected' : '',
      ]"
      @startSelection="onStartSelection"
      @endSelection="onEndSelection"
      @overSelection="onOverSelection"
      @selectEntity="onSelectEntity"
      @changeEntityLabel="onChangeEntityLabel"
      @removeEntity="onRemoveEntity"
      @updateRecordEntities="$emit('updateRecordEntities')"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { indexOf, length } from "stringz";

export default {
  props: {
    entities: {
      type: Array,
    },
    dataset: {
      type: Object,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
    origin: {
      type: String,
      required: true,
    },
  },
  data: function () {
    return {
      selectionStart: undefined,
      selectionEnd: undefined,
      selectionOver: undefined,
      suggestedLabel: undefined,
    };
  },
  computed: {
    visualTokens() {
      const recordHasEmoji = this.record.text.containsEmoji;
      const { visualTokens } = this.record.tokens.reduce(
        ({ visualTokens, startPosition }, token) => {
          const start = recordHasEmoji
            ? indexOf(this.record.text, token, startPosition)
            : this.record.text.indexOf(token, startPosition);
          const end = start + (recordHasEmoji ? length(token) : token.length);
          const hasSpaceAfter = this.record.text.slice(end, end + 1) === " ";
          return {
            visualTokens: [
              ...visualTokens,
              { start, end, text: token, hasSpaceAfter: hasSpaceAfter },
            ],
            startPosition: end,
          };
        },
        {
          visualTokens: [],
          startPosition: 0,
        }
      );
      return Object.freeze(visualTokens);
    },
    textSpans() {
      // TODO Simplify !!!
      const normalizedEntities = (entities, tokens) => {
        const tokenForChar = (character, tokens) => {
          const tokenIdx = tokens.findIndex(
            (token) => token.start <= character && character < token.end
          );
          return tokenIdx >= 0 ? tokenIdx : undefined;
        };
        return entities.map((entity) => {
          const start_token = tokenForChar(entity.start, tokens);
          const end_token = tokenForChar(entity.end - 1, tokens);
          return entity.start_token && entity.end_token
            ? entity
            : { ...entity, start_token, end_token: end_token + 1 };
        });
      };

      let idx = 0;
      let textSpans = [];
      const entities = normalizedEntities(this.entities, this.visualTokens);
      while (idx < this.visualTokens.length) {
        let index = textSpans.length;
        const entityArray = entities.filter(
          (entity) => entity.start_token <= idx && idx < entity.end_token
        );
        const entity = entityArray.find((e) =>
          index > 0 ? e.start >= textSpans[index - 1].end : true
        );
        if (entity) {
          textSpans.push({
            entity,
            tokens: this.visualTokens.slice(
              entity.start_token,
              entity.end_token
            ),
            start: entity.start,
            end: entity.end,
            origin: this.origin,
            hasSpaceAfter: entity.hasSpaceAfter,
          });
          idx = entity.end_token;
        } else {
          const token = this.visualTokens[idx];
          textSpans.push({
            entity: undefined,
            tokens: [token],
            start: token.start,
            end: token.end,
            origin: this.origin,
            hasSpaceAfter: token.hasSpaceAfter,
          });
          idx++;
        }
      }
      return textSpans;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
    }),

    updateAnnotatedEntities(entities) {
      this.updateRecords({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            annotatedEntities: entities,
          },
        ],
      });
    },

    reset(e) {
      if (e.target === this.$refs.list) {
        this.onReset();
      }
    },
    onReset() {
      this.selectionStart = undefined;
      this.selectionEnd = undefined;
      this.selectionOver = undefined;
      this.suggestedLabel = undefined;
    },
    onStartSelection(spanId) {
      this.suggestedLabel = undefined;
      this.selectionStart = spanId;
    },
    onEndSelection(spanId) {
      this.selectionEnd = spanId;
    },
    onOverSelection(spanId) {
      if (
        this.selectionStart !== undefined &&
        this.selectionEnd === undefined
      ) {
        this.selectionOver = spanId;
      } else {
        this.selectionOver = undefined;
      }
    },
    onSelectEntity(entity) {
      const from = Math.min(this.selectionStart, this.selectionEnd);
      const to = Math.max(this.selectionStart, this.selectionEnd);
      const startToken = this.textSpans[from].tokens[0];
      const endToken = this.textSpans[to].tokens.reverse()[0];
      let entities = [...this.entities];
      entities.push({
        start: startToken.start,
        end: endToken.end,
        label: entity,
      });
      this.updateAnnotatedEntities(entities);
      this.onReset();
    },
    onChangeEntityLabel(entity, newLabel) {
      let entities = this.entities.map((ent) => {
        return ent.start === entity.start &&
          ent.end === entity.end &&
          ent.label === entity.label
          ? { ...ent, label: newLabel }
          : ent;
      });
      this.updateAnnotatedEntities(entities);
      this.onReset();
    },
    onRemoveEntity(entity) {
      const found = this.entities.findIndex(
        (ent) =>
          ent.start === entity.start &&
          ent.end === entity.end &&
          ent.label === entity.label
      );
      let entities = [...this.entities];
      entities.splice(found, 1);
      this.updateAnnotatedEntities(entities);
      this.onReset();
    },
    isSelected(i, start, end) {
      const tokenInit = Math.min(start, end);
      const tokenEnd = Math.max(start, end);
      this.suggestEntity();
      if (i >= tokenInit && i <= tokenEnd) {
        return true;
      }
      return false;
    },
    isLastSelected(i, end) {
      if (i === end) {
        return true;
      }
      return false;
    },
    suggestEntity() {
      const spans = [...this.textSpans];
      const from = Math.min(this.selectionStart, this.selectionEnd);
      const to = Math.max(this.selectionStart, this.selectionEnd);
      const startToken = spans[from] && spans[from].tokens[0];
      const endToken =
        spans[to] && spans[to].tokens[spans[to].tokens.length - 1];
      const matchedPrediction =
        this.record.prediction &&
        this.record.prediction.entities.find(
          (ent) =>
            ent.start === (startToken && startToken.start) &&
            ent.end === (endToken && endToken.end)
        );
      if (matchedPrediction) {
        this.suggestedLabel = matchedPrediction.label;
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.content {
  &__input {
    padding-right: 200px;
    ::selection {
      background: none !important;
    }
  }
}
</style>
