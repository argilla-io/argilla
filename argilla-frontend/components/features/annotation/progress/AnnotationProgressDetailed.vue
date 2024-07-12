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
  <div v-if="datasetMetrics.hasMetrics">
    <ul class="my-progress__list">
      <li
        v-for="(status, index) in progressItems"
        :key="index"
        class="my-progress__list__item"
      >
        <span>
          <span
            class="color-bullet"
            :style="{ backgroundColor: status.color }"
          ></span>
          <label class="my-progress__list__name" v-text="status.name" />
        </span>
        <span
          class="my-progress__list__counter"
          v-text="`${getFormattedProgress(status.value)}`"
        />
      </li>
    </ul>
    <p class="team-progress__title" v-text="$t('metrics.progress.team')" />
    <BarProgress
      class="team-progress"
      :loading="false"
      :progress-ranges="progressRanges"
      :progress-completed="datasetMetrics.submitted + datasetMetrics.discarded"
      :total="datasetMetrics.total"
    />
  </div>
</template>

<script>
import { RecordStatus } from "~/v1/domain/entities/record/RecordStatus";
import { useFeedbackTaskProgressViewModel } from "./useFeedbackTaskProgressViewModel";

export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    enableFetch: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    progressItems() {
      return [
        {
          name: RecordStatus.submitted.name,
          color: RecordStatus.submitted.color,
          value: this.datasetMetrics.submitted,
          percent: this.datasetMetrics.percentage.submitted,
        },
        {
          name: RecordStatus.draft.name,
          color: RecordStatus.draft.color,
          value: this.datasetMetrics.draft,
          percent: this.datasetMetrics.percentage.draft,
        },
        {
          name: RecordStatus.discarded.name,
          color: RecordStatus.discarded.color,
          value: this.datasetMetrics.discarded,
          percent: this.datasetMetrics.percentage.discarded,
        },
        {
          name: RecordStatus.pending.name,
          color: RecordStatus.pending.color,
          value: this.datasetMetrics.pending,
          percent: this.datasetMetrics.percentage.pending,
        },
      ];
    },
    progressRanges() {
      return [
        {
          id: "completed",
          name: "completed",
          color: "linear-gradient(90deg, #6A6A6C 0%, #252626 100%)",
          value: this.datasetMetrics.submitted + this.datasetMetrics.discarded,
        },
        {
          id: "pending",
          name: "progress",
          color: "linear-gradient(white)",
          value: this.datasetMetrics.pending + this.datasetMetrics.draft,
        },
      ];
    },
  },
  methods: {
    getFormattedProgress(progress) {
      return progress && this.$options.filters.formatNumber(progress);
    },
  },
  setup(props) {
    return useFeedbackTaskProgressViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
$bullet-size: 8px;
.my-progress {
  display: flex;
  align-items: center;
  gap: $base-space * 4;
  color: $black-54;
  padding: $base-space * 3 0;
  &__donut {
    flex-shrink: 0;
  }
}
.team-progress {
  &__title {
    text-transform: uppercase;
    color: $black-54;
    font-weight: 500;
  }
}
.color-bullet {
  display: inline-flex;
  height: $bullet-size;
  width: $bullet-size;
  margin-right: 4px;
  border-radius: $border-radius-rounded;
}

.my-progress__list {
  display: flex;
  list-style: none;
  gap: $base-space;
  padding-left: 0;
  margin-top: 0;
  margin-bottom: $base-space * 3;
  &__item {
    background: palette(grey, 700);
    display: flex;
    flex-direction: column;
    gap: $base-space;
    padding: $base-space;
    width: 100%;
    border-radius: $border-radius;
  }
  &__name {
    text-transform: capitalize;
    color: $black-54;
    @include font-size(12px);
  }
  &__counter {
    font-weight: 600;
    color: $black-87;
    @include font-size(14px);
  }
}
</style>
