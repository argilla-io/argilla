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
    <p class="metrics__title">Progress</p>
    <div class="metrics__info">
      <p class="metrics__info__name">Total</p>
      <span class="metrics__info__counter">{{
        metrics.progress | percent
      }}</span>
    </div>
    <div class="metrics__numbers">
      <span v-text="metrics.responded" />/{{ metrics.total }}
    </div>
    <BaseProgress
      re-mode="determinate"
      :multiple="true"
      :progress="metrics.percentage.submitted"
      :progress-secondary="metrics.percentage.discarded"
      :progress-tertiary="metrics.percentage.draft"
      :progress-bg="itemColor(0)"
      :color="itemColor(2)"
      :color-secondary="itemColor(1)"
      :color-tertiary="itemColor(3)"
    >
    </BaseProgress>
    <div class="scroll">
      <ul class="metrics__list">
        <li
          v-for="(status, index) in progressItems"
          :key="index"
          class="metrics__list__item"
        >
          <span
            class="color-bullet"
            :style="{ backgroundColor: status.color }"
          ></span>
          <label
            class="metrics__list__name"
            v-text="getFormattedName(status.name)"
          />
          <span
            class="metrics__list__counter"
            v-text="getFormattedProgress(status.progress)"
          />
        </li>
      </ul>
      <slot></slot>
    </div>
  </div>
</template>

<script>
import {
  RECORD_STATUS,
  RECORD_STATUS_COLOR,
} from "@/models/feedback-task-model/record/record.queries";
export default {
  props: {
    metrics: {
      type: Object,
      required: true,
    },
  },
  computed: {
    progressItems() {
      return [
        {
          name: RECORD_STATUS.PENDING,
          color: RECORD_STATUS_COLOR.PENDING,
          progress: this.metrics.pending,
        },
        {
          name: RECORD_STATUS.DRAFT,
          color: RECORD_STATUS_COLOR.DRAFT,
          progress: this.metrics.draft,
        },
        {
          name: RECORD_STATUS.SUBMITTED,
          color: RECORD_STATUS_COLOR.SUBMITTED,
          progress: this.metrics.submitted,
        },
        {
          name: RECORD_STATUS.DISCARDED,
          color: RECORD_STATUS_COLOR.DISCARDED,
          progress: this.metrics.discarded,
        },
      ];
    },
  },
  methods: {
    itemColor(order) {
      return this.progressItems[order]?.color || null;
    },
    getFormattedName(name) {
      return name && this.$options.filters.capitalize(name);
    },
    getFormattedProgress(progress) {
      return progress && this.$options.filters.formatNumber(progress);
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
  height: $base-space;
  width: $base-space;
  border-radius: $border-radius-rounded;
  display: inline-block;
}
:deep() {
  .metrics__title {
    margin-top: 0;
    margin-bottom: $base-space * 4;
    @include font-size(18px);
    font-weight: 600;
  }
  .metrics__subtitle {
    @include font-size(15px);
    font-weight: 600;
  }
  .metrics__info {
    margin-top: 0;
    margin-bottom: $base-space;
    display: flex;
    &__name {
      margin: 0;
    }
    &__counter {
      margin: 0 0 0 auto;
    }
    & + .re-progress__container {
      margin-top: -$base-space;
    }
  }
  .metrics__list {
    list-style: none;
    padding-left: 0;
    margin-bottom: $base-space * 3;
    &__item {
      display: flex;
      align-items: center;
      gap: $base-space;
      margin-bottom: $base-space;
      @include font-size(13px);
    }
    &__name {
      display: block;
      width: calc(100% - 40px);
      hyphens: auto;
      word-break: break-word;
    }
    &__counter {
      margin-right: 0;
      margin-left: auto;
    }
  }
}
</style>
