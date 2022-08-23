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
  <div class="error">
    <div class="panel panel--warning">
      <p class="panel__title">Warning</p>
      <p class="panel__text">
        We cannot currently access <strong>{{ where }}</strong> due to the
        following error: <strong>{{ error.message }}</strong>
      </p>
    </div>
    <base-button v-if="link" class="tertiary outline" :to="link">
      <svgicon name="chevron-left" width="14" height="14" color="#4A4A4A" />
      Back
    </base-button>
  </div>
</template>

<script>
import "assets/icons/chevron-left";

export default {
  props: {
    where: {
      type: String,
      default: undefined,
    },
    link: {
      type: String,
      default: undefined,
    },
    error: {
      type: Object,
      default: undefined,
    },
  },
};
</script>

<style lang="scss" scoped>
.error {
  margin-left: 10vw;
  text-align: left;
}
.panel {
  $this: &;
  position: relative;
  max-width: 700px;
  border: 1px solid palette(grey, 600);
  color: palette(grey, 300);
  border-radius: $border-radius-s;
  padding: 1.2em 5em 1.2em 1.2em;
  @include font-size(14px);
  line-height: 1.5em;
  margin-bottom: 2em;
  text-align: left;
  overflow: hidden;
  &__text {
    margin: 0;
  }
  &.hidden {
    margin: 0;
    padding: 0;
    min-height: 0;
    opacity: 0;
    transition: opacity 0.1s ease-in-out, height 0.3s ease-in-out,
      margin 0.3s ease-in-out, padding 0.3s ease-in-out;
  }
  &--inline,
  &--inline p {
    display: inline-block;
  }
  &--inline {
    margin-bottom: 1em;
    padding: 1em;
  }
  &--block {
    margin-bottom: 1em;
    padding: 1em;
  }
  &--warning {
    margin-top: 5em;
    background: palette(white);
    border: 1px solid $error;
    max-width: calc(100% - 320px);
    #{$this}__title {
      color: $error;
      font-weight: 600;
      margin-top: 0;
      @include font-size(16px);
    }
  }
}
.button {
  display: inline-flex !important;
}
</style>
