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

    <li class="my-progress__item">
      <span>
        <span
          class="color-bullet"
          :style="{ backgroundColor: RecordStatus.submitted.color }"
        ></span>
        <label class="my-progress__name" v-text="RecordStatus.submitted.name" />
      </span>
      <span class="my-progress__counter" v-text="metrics.submitted" />
    </li>
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
$bullet-size: 8px;
.color-bullet {
  display: inline-flex;
  height: $bullet-size;
  width: $bullet-size;
  margin-right: 4px;
  border-radius: $border-radius-rounded;
}

.my-progress {
  &__container {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-right: $base-space * 2;
  }
  &__item {
    display: flex;
    flex-direction: row;
    gap: $base-space;
    padding: $base-space;
    width: auto;
    background: $black-3;
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
