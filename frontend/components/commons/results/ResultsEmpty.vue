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
      <svgicon v-if="emptyIcon" :name="emptyIcon" width="50" height="50" color="#686a6d" />
      <h1 class="empty__title">{{ emptyTitle }}</h1>
      <p v-if="emptyDescription" class="empty__description" v-html="emptyDescription" />
    </span>
  </div>
</template>

<script>
export default {
  props: {
    emptyTitle: {
      type: String,
      default: "0 results found",
    },
    emptyDescription: {
      type: String,
      default: undefined,
    },
    emptyIcon: {
      type: String,
      default: undefined,
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
  margin-top: 0;
  height: 100vh;
  #{$this}__content {
    align-items: center;
    margin: auto;
  }
  &__title {
    @include font-size(30px);
    font-weight: 400;
    color: palette(grey, medium)
  }
  &__description {
    max-width: 600px;
  }
}
</style>
