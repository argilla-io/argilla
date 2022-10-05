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
  <div v-if="annotationsProgress">
    <p class="metrics__title">Progress</p>
    <div class="metrics__info">
      <p class="metrics__info__name">Total</p>
      <span class="metrics__info__counter">{{ progress | percent }}</span>
    </div>
    <div class="metrics__numbers">
      <span>{{ totalAnnotated | formatNumber }}</span
      >/{{ total | formatNumber }}
    </div>
    <base-progress
      re-mode="determinate"
      :multiple="true"
      :progress="(totalValidated * 100) / total"
      :progress-secondary="(totalDiscarded * 100) / total"
    ></base-progress>
    <div class="scroll">
      <ul class="metrics__list">
        <li>
          <span class="color-bullet validated"></span>
          <label class="metrics__list__name">Validated</label>
          <span class="metrics__list__counter">
            {{ totalValidated | formatNumber }}
          </span>
        </li>
        <li>
          <span class="color-bullet discarded"></span>
          <label class="metrics__list__name">Discarded</label>
          <span class="metrics__list__counter">
            {{ totalDiscarded | formatNumber }}
          </span>
        </li>
      </ul>
      <slot></slot>
    </div>
  </div>
</template>

<script>
import { AnnotationProgress } from "@/models/AnnotationProgress";
export default {
  // TODO clean and typify
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    annotationsSum() {
      return this.dataset.results.aggregations.status.Validated;
    },
    annotationsProgress() {
      return AnnotationProgress.find(this.dataset.name);
    },
    totalValidated() {
      return this.annotationsProgress.validated;
    },
    totalDiscarded() {
      return this.annotationsProgress.discarded;
    },
    totalAnnotated() {
      return this.totalValidated + this.totalDiscarded;
    },
    total() {
      return this.annotationsProgress.total;
    },
    datasetName() {
      return this.dataset.name;
    },
    progress() {
      return (
        ((this.totalValidated || 0) + (this.totalDiscarded || 0)) / this.total
      );
    },
  },
};
</script>
<style lang="scss" scoped>
.scroll {
  max-height: calc(100vh - 270px);
  padding-right: 1em;
  margin-right: -1em;
  overflow: auto;
  @extend %hide-scrollbar;
}
.metrics {
  &__numbers {
    margin-bottom: $base-space * 3;
    margin-top: $base-space * 3;
    @include font-size(18px);
    span {
      @include font-size(40px);
      font-weight: 700;
    }
  }
}
.color-bullet {
  height: 10px;
  width: 10px;
  border-radius: 50%;
  display: inline-block;
  margin: 0.3em 0.3em 0.3em 0;
  &.validated {
    background: #4c4ea3;
  }
  &.discarded {
    background: #a1a2cc;
  }
}
</style>
