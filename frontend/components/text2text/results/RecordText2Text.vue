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
    <record-string-text-2-text :record="record" />
    <div>
      <text-2-text-list
        ref="list"
        :datasetId="datasetId"
        :datasetName="datasetName"
        :record="record"
        :predictions="predictionSentences"
        :annotations="annotationSentence"
        :annotation-enabled="interactionsEnabled"
        @reset-record="onReset"
        @annotate="onAnnotate"
        @discard="onDiscard"
      />
    </div>
  </div>
</template>
<script>
import { Text2TextRecord } from "@/models/Text2Text";
import { getText2TextDatasetById } from "@/models/text2text.queries";
import { mapActions } from "vuex";
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
    viewSettings: {
      type: Object,
      required: true,
    },
    record: {
      type: Text2TextRecord,
      required: true,
    },
    isReferenceRecord: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    interactionsEnabled() {
      return this.annotationEnabled && !this.isReferenceRecord;
    },
    annotationEnabled() {
      return this.viewSettings.viewMode === "annotate";
    },
    predictionSentences() {
      return this.record.prediction?.sentences ?? [];
    },
    annotationSentence() {
      return this.record.annotation?.sentences ?? [];
    },
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      validate: "entities/datasets/validateAnnotations",
      resetRecords: "entities/datasets/resetRecords",
    }),

    async onReset() {
      await this.resetRecords({
        dataset: this.getText2TextDataset(),
        records: [
          {
            ...this.record,
          },
        ],
      });
    },
    async onAnnotate({ sentences }) {
      const newRecord = {
        ...this.record,
        status: "Validated",
        annotation: {
          sentences,
        },
      };
      await this.validate({
        dataset: this.getText2TextDataset(),
        // TODO: Move user agent to action
        agent: this.$auth.user.username,
        records: [newRecord],
      });
    },
    onDiscard() {
      this.$emit("discard");
    },
    getText2TextDataset() {
      return getText2TextDatasetById(this.datasetId);
    },
  },
};
</script>

<style scoped lang="scss">
.record {
  display: block;
  @include font-size(16px);
  line-height: 1.6em;
  width: 100%;
  padding: $base-space * 4 200px 20px 20px;
  .list__item--selectable & {
    padding-left: 50px;
  }
  &:hover {
    :deep(.edit) {
      opacity: 1 !important;
      pointer-events: all;
      transition: opacity 0.5s ease-in-out 0.2s !important;
    }
  }
}
</style>
