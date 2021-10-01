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
      v-for="label in labels"
      :key="label.index"
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
    labels: {
      type: Array,
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
  display: inline-flex;
  width: auto;
  background: transparent;
  color: $lighter-color;
  border-radius: 3px;
  padding: 0.2em 1em;
  @include font-size(14px);
  margin-top: 0;
  margin-bottom: 0;
  border: 1px solid transparent;
  margin-right: 0.5em;
}
.predictions {
  margin-top: 1em;
  display: flex;
  flex-wrap: wrap;
  margin-right: -0.8em;
  margin-left: -0.8em;
  .pill {
    height: 40px;
    line-height: 40px;
    display: flex;
    width: 240px;
    align-items: center;
    margin-left: 0.8em;
    margin-right: 0.8em;
    margin-bottom: 1.6em;
    font-weight: bold;
    border: 1px solid palette(grey, smooth);
    border-radius: 5px;
    &__score {
      margin-right: 0;
      margin-left: auto;
    }
  }
}
.pill {
  @extend %pill;
  border: 1px solid $line-medium-color;
  color: $font-medium-color;
  margin-bottom: 0.5em;
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
    font-weight: bold;
    margin-left: 1em;
  }
  &.active {
    border-color: $secondary-color;
  }
}
</style>
