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
    <div class="record--left record__item">
      <record-string-text-2-text
        :query-text="dataset.query.text"
        :text="record.text"
      />
      <div>
        <text-2-text-list
          ref="list"
          :status="record.status"
          :predictions="predictionSentences"
          :annotations="initialAnnotations"
          :sentences-origin="sentencesOrigin"
          :annotation-enabled="annotationEnabled"
          @update-record="updateRecordSentences"
          @change-visible-sentences="onChangeSentences"
          @reset-initial-record="onResetInitialRecord"
          @annotate="onAnnotate"
        />
      </div>
    </div>
  </div>
</template>
<script>
import { getUsername } from "@/models/User";
import { Text2TextRecord, Text2TextDataset } from "@/models/Text2Text";
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      type: Text2TextDataset,
      required: true,
    },
    record: {
      type: Text2TextRecord,
      required: true,
    },
  },
  data: () => ({
    sentencesOrigin: undefined,
    initialRecord: {},
  }),
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
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
    this.initializeSentenceOrigin();
    this.initialRecord = Object.assign({}, this.record);
  },
  watch: {
    annotationEnabled(oldValue, newValue) {
      if (oldValue !== newValue) {
        this.initializeSentenceOrigin();
      }
    }
  },
  methods: {
    ...mapActions({
      updateRecords: "entities/datasets/updateDatasetRecords",
      validate: "entities/datasets/validateAnnotations",
    }),

    initializeSentenceOrigin() {
      if (this.annotationEnabled) {
        if (this.annotationSentences.length) {
          this.sentencesOrigin = "Annotation";
        } else if (this.predictionSentences.length) {
          this.sentencesOrigin = "Prediction";
        }
      } else {
        if (this.predictionSentences.length) {
          this.sentencesOrigin = "Prediction";
        } else if (this.annotationSentences.length) {
          this.sentencesOrigin = "Annotation";
        }
      }
    },

    onChangeSentences() {
      this.sentencesOrigin !== "Annotation"
        ? (this.sentencesOrigin = "Annotation")
        : (this.sentencesOrigin = "Prediction");
    },
    async updateRecordSentences({ sentences }) {
      await this.updateRecords({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            selected: true,
            status: "Edited",
            annotation: {
              sentences,
            },
          },
        ],
      });
    },
    async onResetInitialRecord() {
      await this.updateRecords({
        dataset: this.dataset,
        records: [
          {
            ...this.initialRecord,
            selected: false,
          },
        ],
      });
    },
    async onAnnotate({ sentences }) {
      this.sentencesOrigin = "Annotation";
      const newRecord = {
        ...this.record,
        status: "Validated",
        annotation: {
          sentences,
        },
      };
      this.initialRecord = newRecord;
      await this.validate({
        dataset: this.dataset,
        agent: getUsername(this.$auth),
        records: [newRecord],
      });
    },
  },
};
</script>

<style scoped lang="scss">
.record {
  display: flex;
  &__item {
    display: block;
    @include font-size(16px);
    line-height: 1.6em;
    &:hover {
      ::v-deep .button-primary--outline {
        opacity: 1 !important;
        transition: opacity 0.5s ease-in-out 0.2s !important;
      }
    }
  }
  &--left {
    width: 100%;
    padding: 44px 20px 20px 20px;
    .list__item--annotation-mode & {
      padding-left: 65px;
    }
  }
}
</style>
