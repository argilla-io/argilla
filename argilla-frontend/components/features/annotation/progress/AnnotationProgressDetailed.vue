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
  <div>
    <ul class="my-progress__list">
      <template v-if="!metrics.hasMetrics">
        <StatusCounterSkeleton
          v-for="(status, index) in progressItems"
          :key="index"
          class="my-progress__status--skeleton"
        />
      </template>
      <template v-else>
        <StatusCounter
          v-for="(status, index) in progressItems"
          :key="index"
          class="my-progress__status"
          :color="status.color"
          :name="status.name"
          :value="status.value"
        />
      </template>
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
  setup() {
    return useAnnotationProgressViewModel();
  },
};
</script>

<style lang="scss" scoped>
$statusCounterMinHeight: 60px;
.my-progress {
  display: flex;
  align-items: center;
  gap: $base-space * 4;
  color: var(--fg-secondary);
  padding: $base-space * 3 0;
  &__donut {
    flex-shrink: 0;
  }
}
.team-progress {
  &__title {
    text-transform: uppercase;
    color: var(--fg-secondary);
    font-weight: 500;
  }
}

.my-progress {
  &__list {
    display: flex;
    list-style: none;
    gap: $base-space;
    padding-left: 0;
    margin-top: 0;
    margin-bottom: $base-space * 3;
  }
  &__status.status-counter {
    flex-direction: column;
    width: 100%;
  }
  &__status--skeleton {
    @extend .my-progress__status;
    height: $statusCounterMinHeight;
  }
}
</style>
