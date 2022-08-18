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
  <span :class="['entity-label', color, isPrediction ? '--prediction' : null]">
    {{ label }}
    <span v-if="shortcut" class="shortcut">[{{ shortcut }}]</span>
  </span>
</template>

<script>
export default {
  props: {
    color: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    shortcut: {
      type: String,
      default: undefined,
    },
    isPrediction: {
      type: Boolean,
      default: false,
    },
  },
};
</script>

<style scoped lang="scss">
.entity-label {
  padding: 0.3em;
  position: relative;
  display: inline-flex;
  align-items: center;
  max-height: 28px;
  font-weight: 600;
  color: palette(grey, 200);
  .shortcut {
    @include font-size(14px);
    font-weight: lighter;
    margin-left: $base-space * 2;
  }
}
// ner colors

$colors: 50;
$hue: 360;
@for $i from 1 through $colors {
  $rcolor: hsla(($colors * $i) + calc($hue * $i / $colors), 100%, 88%, 1);
  .color_#{$i - 1} {
    background: $rcolor;
    &.--prediction {
      background: none;
      border-bottom: 5px solid $rcolor;
      padding: 0.3em 0;
    }
  }
}
</style>
