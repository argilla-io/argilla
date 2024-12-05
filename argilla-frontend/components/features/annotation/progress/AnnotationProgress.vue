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
  <div class="my-progress__container">
    <TeamProgress :datasetId="datasetId" />
    <StatusCounterSkeleton
      v-if="!metrics.hasMetrics"
      class="my-progress__status--skeleton"
    />
    <div v-else class="my-progress__share">
      <Share v-if="isShareYourProgressEnabled && canSeeShare" />
      <StatusCounter
        :ghost="true"
        :rainbow="isShareYourProgressEnabled && shouldShowSubmittedAnimation"
        class="my-progress__status"
        :color="RecordStatus.submitted.color"
        :name="RecordStatus.submitted.name"
        :value="metrics.submitted"
      />
    </div>
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
  },
  computed: {
    RecordStatus() {
      return RecordStatus;
    },
  },
  setup(props) {
    return useAnnotationProgressViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
$statusCounterMinWidth: 110px;
$statusCounterMinHeight: 30px;
.my-progress {
  &__container {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-right: $base-space * 2;
  }
  &__status {
    &--skeleton {
      min-width: $statusCounterMinWidth;
      min-height: $statusCounterMinHeight;
    }
  }
  &__share {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: end;
    gap: $base-space;
  }
}
</style>
