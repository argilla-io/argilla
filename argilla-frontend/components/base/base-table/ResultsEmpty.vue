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
  <div class="empty">
    <span class="empty__content">
      <svgicon v-if="icon" :name="icon" width="50" height="50" />
      <h1 class="empty__title">{{ title }}</h1>
      <p v-if="message" class="empty__message" v-html="message" />
    </span>
  </div>
</template>

<script>
import "assets/icons/smile-sad";
export default {
  props: {
    title: {
      type: String,
      default: "0 results found",
    },
    message: {
      type: String,
      default: undefined,
    },
    icon: {
      type: String,
      default: "smile-sad",
    },
  },
};
</script>

<style lang="scss" scoped>
.empty {
  $this: &;
  text-align: center;
  width: 100%;
  display: flex;
  height: calc(100vh - 400px);
  #{$this}__content {
    align-items: center;
    margin: auto;
  }
  &__title {
    @include font-size(30px);
    font-weight: 400;
    color: var(--fg-tertiary);
  }
  &__message {
    max-width: 600px;
  }
}
.svg-icon {
  fill: var(--fg-tertiary);
}
</style>
