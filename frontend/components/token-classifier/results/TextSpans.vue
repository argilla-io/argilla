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
  <div>
    <div v-if="textSpans.length" ref="list" class="content__input">
      <TextSpan
        v-for="(token, i) in textSpans"
        :key="i"
        :record="record"
        :span-id="i"
        :spans="textSpans"
        :dataset="dataset"
        :class="isSelected(i) ? 'selected' : ''"
        @startSelection="onStartSelection"
        @endSelection="onEndSelection"
        @selectEntity="onSelectEntity"
        @changeEntityLabel="onChangeEntityLabel"
        @removeEntity="onRemoveEntity"
        @updateRecordEntities="$emit('updateRecordEntities')"
      />
    </div>
  </div>
</template>

<script>
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
    agent: {
      type: String,
    },
    entities: {
      type: Array,
    },
  },
  data: function () {
    return {
      selectionStart: undefined,
      selectionEnd: undefined,
    };
  },
  computed: {
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
      const entities = normalizedEntities(
        this.entities,
        this.record.visualTokens
      );
      while (idx < this.record.visualTokens.length) {
        const entity = entities.find(
          (entity) => entity.start_token <= idx && idx < entity.end_token
        );
        if (entity) {
          textSpans.push({
            entity,
            tokens: this.record.visualTokens.slice(
              entity.start_token,
              entity.end_token
            ),
            start: entity.start,
            end: entity.end,
            agent: this.agent,
          });
          idx = entity.end_token;
        } else {
          const token = this.record.visualTokens[idx];
          textSpans.push({
            entity: undefined,
            tokens: [token],
            start: token.start,
            end: token.end,
            agent: this.agent,
          });
          idx++;
        }
      }
      return textSpans;
    },
  },
  methods: {
    onReset() {
      this.selectionStart = undefined;
      this.selectionEnd = undefined;
    },
    onStartSelection(spanId) {
      this.selectionStart = spanId;
    },
    onEndSelection(spanId) {
      this.selectionEnd = spanId;
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
      this.$emit("updateRecordEntities", entities);
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
      this.$emit("updateRecordEntities", entities);
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
      this.$emit("updateRecordEntities", entities);
      this.onReset();
    },
    isSelected(i) {
      const init = Math.min(this.selectionStart, this.selectionEnd);
      const end = Math.max(this.selectionStart, this.selectionEnd);
      if (i >= init && i <= end) {
        return true;
      }
      return false;
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  padding: 44px 20px 20px 20px;
  display: block;
  margin-bottom: 0; // white-space: pre-line;
  white-space: pre-wrap;
  @include font-size(16px);
  line-height: 1.6em;
  .list__item--annotation-mode & {
    padding-left: 65px;
  }
}
.content {
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
