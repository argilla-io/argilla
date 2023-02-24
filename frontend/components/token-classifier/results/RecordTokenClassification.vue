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
      <div class="origins">
        <text-spans-static
          v-if="record.prediction"
          :v-once="datasetQuery.score ? false : true"
          key="prediction"
          origin="prediction"
          class="prediction"
          :datasetName="datasetName"
          :datasetEntities="labels"
          :datasetQuery="datasetQuery"
          :record="record"
          :visualTokens="visualTokens"
          :entities="getEntitiesByOrigin('prediction')"
        />
        <text-spans
          key="annotation"
          :viewSettings="viewSettings"
          origin="annotation"
          class="annotation"
          :datasetId="datasetId"
          :datasetName="datasetName"
          :datasetEntities="labels"
          :datasetLastSelectedEntity="datasetLastSelectedEntity"
          :record="record"
          :visualTokens="visualTokens"
          :entities="getEntitiesByOrigin('annotation')"
        />
      </div>
      <div
        class="content__actions-buttons"
        v-if="interactionsEnabled && record.status !== 'Validated'"
      >
        <base-button class="primary" @click="onValidate(record)">
          {{ record.status === "Edited" ? "Save" : "Validate" }}
        </base-button>
        <base-button
          :disabled="!record.annotatedEntities.length"
          class="primary outline"
          @click="onClearAnnotations()"
        >
          Clear annotations
        </base-button>
      </div>
    </div>
  </div>
</template>

<script>
import { indexOf, length } from "stringz";
import { mapActions } from "vuex";
import { getTokenClassificationDatasetById } from "@/models/tokenClassification.queries";
import { getAllLabelsByDatasetId } from "@/models/globalLabel.queries";

export default {
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetName: {
      type: String,
      required: true,
    },
    datasetQuery: {
      type: Object,
      required: true,
    },
    datasetLastSelectedEntity: {
      type: Object,
      required: true,
    },
    viewSettings: {
      type: Object,
      required: true,
    },
    record: {
      type: Object,
      required: true,
    },
    isReferenceRecord: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isSortAsc: true,
      sortBy: "text",
    };
  },
  computed: {
    interactionsEnabled() {
      return this.annotationEnabled && !this.isReferenceRecord;
    },
    annotationEnabled() {
      return this.viewSettings.viewMode === "annotate";
    },
    labels() {
      return getAllLabelsByDatasetId(
        this.datasetId,
        this.sortBy,
        this.isSortAsc
      );
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
          const end = start + (recordHasEmoji ? length(token) : token.length);
          const nextStart = recordHasEmoji
            ? indexOf(this.record.text, this.record.tokens[index + 1], end)
            : this.record.text.indexOf(this.record.tokens[index + 1], end);
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
  methods: {
    ...mapActions({
      validate: "entities/datasets/validateAnnotations",
      updateRecords: "entities/datasets/updateDatasetRecords",
    }),
    getEntitiesByOrigin(origin) {
      if (this.interactionsEnabled) {
        return origin === "annotation"
          ? this.record.annotatedEntities
          : (this.record.prediction && this.record.prediction.entities) || [];
      } else {
        return this.record[origin]
          ? this.record[origin].entities.map((obj) => ({
              ...obj,
              origin: origin,
            }))
          : [];
      }
    },
    async onValidate(record) {
      await this.validate({
        // TODO: Move this as part of token classification dataset logic
        dataset: this.getTokenClassificationDataset(),
        agent: this.$auth.user.username,
        records: [
          {
            ...record,
            annotatedEntities: undefined,
            annotation: {
              entities: record.annotatedEntities,
              origin: "annotation",
            },
          },
        ],
      });
    },
    onClearAnnotations() {
      this.updateRecords({
        dataset: this.getTokenClassificationDataset(),
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            annotatedEntities: [],
          },
        ],
      });
    },
    getTokenClassificationDataset() {
      return getTokenClassificationDatasetById(this.datasetId);
    },
  },
};
</script>

<style lang="scss" scoped>
.record {
  padding: 26px 200px 50px 50px;
  display: block;
  margin-bottom: 0;
  @include font-size(16px);
  line-height: 34px;
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
    .button {
      margin: 1.5em 0 0 0;
      & + .button {
        margin-left: $base-space;
      }
    }
  }
}

.origins > .prediction {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  :deep() {
    .span__text {
      color: transparent;
      & > * {
        color: $black-54;
      }
    }
    .highlight__content {
      color: transparent;
    }
  }
  :deep(.highlight-text) {
    opacity: 1;
  }
}
</style>
