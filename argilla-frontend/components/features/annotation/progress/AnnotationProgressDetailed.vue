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
  <div v-if="metrics.hasMetrics">
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
        <span class="my-progress__list__counter" v-text="status.value" />
      </li>
    </ul>
    <p class="team-progress__title" v-text="$t('metrics.progress.team')" />
    <TeamProgress
      visibleProgressValues
      :datasetId="datasetId"
      :show-tooltip="false"
    />
  </div>
</template>

<script>
import { RecordStatus } from "~/v1/domain/entities/record/RecordStatus";
import { useAnnotationProgressViewModel } from "./useAnnotationProgressViewModel";

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
          name: RecordStatus.pending.name,
          color: RecordStatus.pending.color,
          value: this.metrics.pending,
          percent: this.metrics.percentage.pending,
        },
        {
          name: RecordStatus.draft.name,
          color: RecordStatus.draft.color,
          value: this.metrics.draft,
          percent: this.metrics.percentage.draft,
        },
        {
          name: RecordStatus.discarded.name,
          color: RecordStatus.discarded.color,
          value: this.metrics.discarded,
          percent: this.metrics.percentage.discarded,
        },
        {
          name: RecordStatus.submitted.name,
          color: RecordStatus.submitted.color,
          value: this.metrics.submitted,
          percent: this.metrics.percentage.submitted,
        },
      ];
    },
  },
  setup(props) {
    return useAnnotationProgressViewModel(props);
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
    background: $black-3;
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
