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
    <p
      :class="['pill', isPredictedAs(label) ? 'active' : '']"
      :title="label.class"
    >
      <span class="pill__text">{{ label.class }} </span>
      <span v-if="showScore" class="pill__score">
        <span class="radio-data__score">{{ label.score | percent }}</span>
      </span>
    </p>
  </div>
</template>

<script>
export default {
  props: {
    label: {
      type: Object,
      required: true,
    },
    predictedAs: {
      type: Array,
    },
    showScore: {
      type: Boolean,
      default: false,
    },
    annotationLabels: {
      type: Array,
      default: () => [],
    },
  },
  methods: {
    isPredictedAs(label) {
      return this.predictedAs ? this.predictedAs.includes(label.class) : null;
    },
  },
};
</script>

<style lang="scss" scoped>
%pill {
  display: flex;
  align-items: center;
  width: auto;
  background: transparent;
  height: 40px;
  line-height: 40px;
  color: $lighter-color;
  border-radius: 8px;
  padding: 0.2em 0.5em;
  @include font-size(14px);
  border: 1px solid transparent;
  margin: 3.5px;
  font-weight: 600;
}

.pill {
  @extend %pill;
  border: 1px solid palette(grey, smooth);
  color: $font-medium-color;
  line-height: 1.4em;
  &__container {
    display: flex;
    margin-bottom: 1em;
  }
  &__text {
    display: inline-block;
    max-width: 200px;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
  }
  &__score {
    margin-left: 1em;
  }
  &.active {
    background: #f4f5f6;
  }
}
</style>
