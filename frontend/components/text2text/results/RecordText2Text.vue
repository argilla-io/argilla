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
      <text-2-text-annotation-area
        v-if="annotationEnabled"
        :prediction="predictionSentences"
        :annotation="annotationSentences"
        :status="record.status"
        @annotate="onAnnotate"
      />
      <text-2-text-exploration-area
        v-else
        :prediction="predictionSentences"
        :annotation="annotationSentences"
      />
    </div>
  </div>
</template>
<script>
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
  data: () => ({}),
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
  },
  methods: {
    ...mapActions({
      validate: "entities/datasets/validateAnnotations",
    }),

    async onAnnotate({ sentences }) {
      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user,
        records: [
          {
            ...this.record,
            status: "Validated",
            annotation: {
              sentences,
            },
          },
        ],
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
      ::v-deep .button-primary--outline, ::v-deep .button-clear {
        opacity: 1 !important;
        transition: opacity 0.5s ease-in-out 0.2s !important;
      }
    }
  }
  &--left {
    width: 100%;
    padding: 2em 2em 0.5em 2em;
    .list__item--annotation-mode & {
      padding-left: 65px;
    }
  }
}
</style>
