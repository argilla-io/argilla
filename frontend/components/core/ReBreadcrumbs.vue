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
  <ul class="breadcrumbs">
    <li>
      <NuxtLink
        v-for="breadcrumb in breadcrumbs"
        :key="breadcrumb.name"
        class="breadcrumbs__item"
        :to="breadcrumb.link"
      >
        {{ breadcrumb.name }}
      </NuxtLink>
    </li>
  </ul>
</template>

<script>
export default {
  props: {
    breadcrumbs: {
      type: Array,
    },
  },
};
</script>

<style lang="scss" scoped>
.breadcrumbs {
  margin-right: auto;
  margin-left: 1em;
  display: inline-block;
  list-style: none;
  padding-left: 0;
  font-weight: normal;
  &__item {
    margin: auto 0.5em auto auto;
    color: $lighter-color;
    text-decoration: none;
    outline: none;
    &:not(:last-child):after {
      content: "/";
      margin-left: 0.5em;
    }
    &:last-child {
      font-weight: 600;
    }
  }
}
</style>
