<template>
  <div class="record">
    <div v-if="textSpans.length" ref="list">
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
        @reset="onReset"
      />
    </div>
    <RecordExtraActions
      :allow-change-status="annotationEnabled"
      :record="record"
      @onChangeRecordStatus="onChangeRecordStatus"
      @onShowMetadata="$emit('onShowMetadata')"
    />
  </div>
</template>

<script>
import { mapActions } from "vuex";

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
  data: function () {
    return {
      selectionStart: undefined,
      selectionEnd: undefined,
    };
  },
  computed: {
    entities() {
      let entities = [];
      if (this.record.annotation) {
        entities = this.record.annotation.entities;
      } else if (this.record.prediction) {
        entities = this.record.prediction.entities;
      }
      return entities;
    },
    agent() {
      if (this.record.annotation) {
        return this.record.annotation.agent;
      }
      if (this.record.prediction) {
        return this.record.prediction.agent;
      }
      return undefined;
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
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateRecords",
      discard: "entities/datasets/discardAnnotations",
    }),

    async onChangeRecordStatus(status) {
      switch (status) {
        case "Discarded":
          await this.discard({ dataset: this.dataset, records: [this.record] });
          break;
        default:
          console.warn("waT?", status);
      }
    },
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
    updateRecordEntities(entities) {
      this.updateRecords({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            annotation: {
              entities,
              agent: this.$auth.user,
            },
          },
        ],
      });
      this.onReset();
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
      this.updateRecordEntities(entities);
    },
    onChangeEntityLabel(entity, newLabel) {
      let entities = this.entities.map((ent) => {
        return ent.start === entity.start &&
          ent.end === entity.end &&
          ent.label === entity.label
          ? { ...ent, label: newLabel }
          : ent;
      });
      this.updateRecordEntities(entities);
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
      this.updateRecordEntities(entities);
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
  padding: 2em 2em 0.5em 2em;
  display: block;
  margin-bottom: 0; // white-space: pre-line;
  white-space: pre-wrap;
  @include font-size(16px);
  line-height: 1.6em;
  .list__item--annotation-mode & {
    padding-left: 4em;
  }
}
</style>
