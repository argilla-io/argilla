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
        @annotate="onAnnotate"
        @edit="onEdit"
      />
      <ClassifierExplorationArea v-else :record="record" />
    </div>
    <div v-if="!annotationEnabled && record.annotation" class="record__labels">
      <svgicon
        v-if="record.predicted"
        :class="['icon__predicted', record.predicted]"
        width="20"
        height="20"
        :name="record.predicted ? 'predicted-ko' : 'predicted-ok'"
      ></svgicon>
      <re-tag v-for="label in record.annotation.labels" :key="label.class" bg-color="#f5f5f6" :name="label.class" />
    </div>
  </div>
</template>
<script>
import "assets/icons/predicted-ok";
import "assets/icons/predicted-ko";
import {
  TextClassificationRecord,
  TextClassificationDataset,
} from "@/models/TextClassification";
import { mapActions } from "vuex";
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
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
  methods: {
    ...mapActions({
      validate: "entities/datasets/validateAnnotations",
      edit: "entities/datasets/editAnnotations",
    }),

    async onEdit({ labels }) {
      await this.edit({
        dataset: this.dataset,
        records: [
          {
            ...this.record,
            status: "Edited",
            annotation: {
              agent: this.$auth.user,
              labels,
            },
          },
        ],
      });
    },

    async onAnnotate({ labels }) {
      await this.validate({
        dataset: this.dataset,
        agent: this.$auth.user,
        records: [
          {
            ...this.record,
            status: ["Discarded", "Validated"].includes(this.record.status)
              ? "Edited"
              : this.record.status,
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
  },
};
</script>

<style scoped lang="scss">
.record {
  display: flex;
  &--left {
    width: 100%;
    padding: 2em 2em 0.5em 2em;
    .list__item--annotation-mode & {
      padding-left: 65px;
    }
  }
  &__labels {
    position: relative;
    margin-left: 2em;
    width: 170px;
    margin-bottom: -3em;
    display: block;
    height: 100%;
    overflow: auto;
    text-align: right;
    padding: 1em;
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
      fill: $error;
    }
    &.ok {
      fill: $success;
    }
  }
}
</style>
