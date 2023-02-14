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
        :annotations="initialAnnotations"
        :annotation-enabled="interactionsEnabled"
        @update-initial-record="initializeInitialRecord"
        @reset-initial-record="onResetInitialRecord"
        @annotate="onAnnotate"
        @discard="onDiscard"
      />
    </div>
  </div>
</template>
<script>
import { IdState } from "vue-virtual-scroller";
import { Text2TextRecord } from "@/models/Text2Text";
import { getText2TextDatasetById } from "@/models/text2text.queries";
import { mapActions } from "vuex";
export default {
  mixins: [
    IdState({
      // You can customize this
      idProp: (vm) => `${vm.datasetName}-${vm.record.id}`,
    }),
  ],
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
  idState() {
    return {
      initialRecord: {},
    };
  },
  computed: {
    initialRecord: {
      get() {
        return this.idState.initialRecord;
      },
      set(newValue) {
        this.idState.initialRecord = newValue;
      },
    },
    interactionsEnabled() {
      return this.annotationEnabled && !this.isReferenceRecord;
    },
    annotationEnabled() {
      return this.viewSettings.viewMode === "annotate";
    },
    annotationSentences() {
      return this.record.annotation ? this.record.annotation.sentences : [];
    },
    predictionSentences() {
      return this.record.prediction ? this.record.prediction.sentences : [];
    },
    initialAnnotations() {
      return this.initialRecord.annotation
        ? this.initialRecord.annotation.sentences
        : [];
    },
  },
  mounted() {
    if (!typeof this.records === Text2TextRecord) {
      this.record = Text2TextRecord(this.record);
    }
    this.initializeInitialRecord();
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      validate: "entities/datasets/validateAnnotations",
    }),

    initializeInitialRecord() {
      this.initialRecord = Object.assign({}, this.record);
    },
    async onResetInitialRecord() {
      await this.updateRecords({
        dataset: this.getText2TextDataset(),
        records: [
          {
            ...this.initialRecord,
            selected: false,
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
      this.initialRecord = newRecord;
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
  padding: 20px 200px 20px 50px;
  &:hover {
    :deep(.edit) {
      opacity: 1 !important;
      pointer-events: all;
      transition: opacity 0.5s ease-in-out 0.2s !important;
    }
  }
}
</style>
