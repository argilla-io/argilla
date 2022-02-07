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
    <!-- annotation labels and prediction status -->
    <div class="record--left">
      <!-- record text -->
      <RecordInputs
        :predicted="record.predicted"
        :data="record.inputs"
        :explanation="record.explanation"
        :query-text="dataset.query.text"
      />
      <ClassifierAnnotationArea
        v-if="annotationEnabled"
        :dataset="dataset"
        :record="record"
        @validate="validateLabels"
        @reset="resetLabels"
      />
      <ClassifierExplorationArea v-else :dataset="dataset" :record="record" />
      <div v-if="annotationEnabled" class="content__actions-buttons">
        <re-button
          v-if="allowValidate"
          class="button-primary"
          @click="onValidate(record)"
          >Validate</re-button
        >
      </div>
    </div>

    <div v-if="!annotationEnabled" class="record__labels">
      <template v-if="record.annotation">
        <svgicon
          v-if="record.predicted && !labellingRulesView"
          :class="['icon__predicted', record.predicted]"
          width="20"
          height="20"
          :name="record.predicted === 'ko' ? 'predicted-ko' : 'predicted-ok'"
        ></svgicon>
        <re-tag
          v-for="label in record.annotation.labels"
          :key="label.class"
          :name="label.class"
        />
      </template>
    </div>
  </div>
</template>

<script>
import "assets/icons/predicted-ok";
import "assets/icons/predicted-ko";
import { mapActions } from "vuex";
import {
  TextClassificationRecord,
  TextClassificationDataset,
} from "@/models/TextClassification";
export default {
  props: {
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
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    labellingRulesView() {
      return this.dataset.viewSettings.viewMode === "labelling-rules";
    },
    allowValidate() {
      const isBinary =
        this.dataset.labels.length === 2 && !this.dataset.isMultiLabel;
      return (
        this.record.status !== "Validated" &&
        !isBinary &&
        (this.record.annotation ||
          this.record.prediction ||
          this.dataset.isMultiLabel)
      );
    },
  },
  methods: {
    ...mapActions({
      validateAnnotations: "entities/datasets/validateAnnotations",
      resetAnnotations: "entities/datasets/resetAnnotations",
    }),
    async resetLabels() {
      await this.resetAnnotations({
        dataset: this.dataset,
        records: [this.record],
      });
    },

    async validateLabels({ labels }) {
      await this.validateAnnotations({
        dataset: this.dataset,
        agent: this.$auth.user.username,
        records: [
          {
            ...this.record,
            annotation: {
              labels: labels.map((label) => ({
                class: label,
                score: 1.0,
              })),
            },
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
        dataset: this.dataset,
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
  },
};
</script>

<style scoped lang="scss">
.record {
  display: flex;
  &--left {
    width: 100%;
    padding: 15px 20px 20px 20px;
    .list__item--annotation-mode & {
      padding-left: 65px;
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
  }
}

.icon {
  &__predicted {
    display: block;
    text-align: right;
    margin-right: 0;
    margin-left: auto;
    margin-bottom: 1em;
    &.ko {
      transform: scaleX(-1);
      fill: $error;
    }
    &.ok {
      fill: $success;
    }
  }
}

.content {
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
