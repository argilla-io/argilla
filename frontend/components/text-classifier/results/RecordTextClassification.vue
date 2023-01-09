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
    <div class="record--left">
      <record-inputs :record="record" />
      <classifier-annotation-area
        v-if="annotationEnabled"
        :inputLabels="dataset.labels"
        :datasetName="dataset.name"
        :isMultiLabel="dataset.isMultiLabel"
        :paginationSize="paginationSize"
        :record="record"
        @validate="validateLabels"
        @reset="resetLabels"
      />
      <classifier-exploration-area
        v-else
        :dataset="dataset"
        :datasetName="dataset.name"
        :paginationSize="paginationSize"
        :record="record"
      />
      <div v-if="annotationEnabled" class="content__actions-buttons">
        <base-button
          v-if="allowValidate"
          class="primary"
          @click="onValidate(record)"
          >Validate</base-button
        >
      </div>
    </div>

    <div v-if="!annotationEnabled" class="record__labels">
      <template v-if="record.annotation">
        <base-tag
          v-for="label in record.annotation.labels"
          :key="label.class"
          :name="label.class"
        />
      </template>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import { DatasetViewSettings as ViewSettingsModel } from "@/models/DatasetViewSettings";
import {
  TextClassificationRecord,
  TextClassificationDataset,
} from "@/models/TextClassification";
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
    dataset: {
      type: TextClassificationDataset,
      required: true,
    },
    record: {
      type: TextClassificationRecord,
      required: true,
    },
  },
  data: () => ({}),
  computed: {
    viewSettings() {
      return ViewSettingsModel.query().with("pagination").whereId(this.datasetName).first();
    },
    isMultiLabel() {
      return this.getTextClassificationDataset().isMultiLabel;
    },
    viewMode() {
      return this.viewSettings.viewMode;
    },
    annotationEnabled() {
      return this.viewMode === "annotate";
    },
    labellingRulesView() {
      return this.viewMode === "labelling-rules";
    },
    allowValidate() {
      return (
        this.record.status !== "Validated" &&
        (this.record.annotation || this.record.prediction || this.isMultiLabel)
      );
    },
    paginationSize() {
      return this.viewSettings?.pagination.size;
    },
  },
  methods: {
    ...mapActions({
      validateAnnotations: "entities/datasets/validateAnnotations",
      resetAnnotations: "entities/datasets/resetAnnotations",
    }),
    async resetLabels() {
      await this.resetAnnotations({
        dataset: this.getTextClassificationDataset(),
        records: [this.record],
      });
    },

    async validateLabels({ labels }) {
      const annotation = {
        labels: labels.map((label) => ({
          class: label,
          score: 1.0,
        })),
      };

      await this.validateAnnotations({
        dataset: this.getTextClassificationDataset(),
        agent: this.$auth.user.username,
        records: [
          {
            ...this.record,
            annotation,
          },
        ],
      });
    },
    async onValidate(record) {
      let modelPrediction = {};
      modelPrediction.labels = record.predicted_as.map((pred) => ({
        class: pred,
        score: 1,
      }));
      // TODO: do not validate records without labels
      await this.validateAnnotations({
        dataset: this.getTextClassificationDataset(),
        agent: this.$auth.user.username,
        records: [
          {
            ...record,
            annotation: {
              ...(record.annotation || modelPrediction),
            },
          },
        ],
      });
    },
    getTextClassificationDataset() {
      return TextClassificationDataset.query().whereId(this.datasetId).first();
    },
  },
};
</script>

<style scoped lang="scss">
.record {
  display: flex;
  &--left {
    width: 100%;
    padding: 50px 20px 50px 50px;
    .list__item--annotation-mode & {
      padding-right: 240px;
    }
  }
  &__labels {
    position: relative;
    margin-left: 2em;
    width: 300px;
    display: block;
    height: 100%;
    overflow: auto;
    text-align: right;
    padding: 4em 1.4em 1em 1em;
    @extend %hide-scrollbar;
  }
}
.content {
  &__actions-buttons {
    margin-right: 0;
    margin-left: auto;
    display: flex;
    min-width: 20%;
    .button {
      margin: 1.5em auto 0 0;
      & + .button {
        margin-left: $base-space * 2;
      }
    }
  }
}
</style>
