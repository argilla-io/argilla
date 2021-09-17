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
  <div class="topbar">
    <RubrixIsotipo v-if="!title" />
    <NuxtLink v-else :to="{ name: 'datasets' }">
      <p class="title">
        {{ title }}
      </p>
    </NuxtLink>
    <slot />
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: undefined,
    },
    icon: {
      type: String,
      default: undefined,
    },
  },
  data: () => ({}),
};
</script>

<style lang="scss" scoped>
.topbar {
  width: 100%;
  display: flex;
  align-items: center;
  min-height: 45px;
  position: relative;
  background: $primary-color;
  border-bottom: 1px solid $line-light-color;
  color: $lighter-color;
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
  a {
    text-decoration: none;
  }
  .title {
    color: $lighter-color;
    @include font-size(18px);
    font-weight: 900;
    font-family: $ff;
    text-decoration: none;
    .svg-icon {
      margin-right: 0.5em;
    }
  }
}
</style>
