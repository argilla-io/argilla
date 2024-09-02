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
  <div class="breadcrumbs">
    <ul>
      <li v-for="breadcrumb in filteredBreadcrumbs" :key="breadcrumb.name">
        <nuxt-link
          class="breadcrumbs__item"
          v-if="breadcrumb.link"
          :to="breadcrumb.link"
          >{{ breadcrumb.name }}
        </nuxt-link>
        <span
          v-else
          class="breadcrumbs__item --action"
          @click="onBreadcrumbAction(breadcrumb)"
          >{{ breadcrumb.name }}</span
        >
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: {
    breadcrumbs: {
      type: Array,
      default: () => [],
    },
    copyButton: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    filteredBreadcrumbs() {
      return this.breadcrumbs.filter((breadcrumb) => breadcrumb.name);
    },
  },
  methods: {
    onBreadcrumbAction(breadcrumb) {
      this.$emit("breadcrumb-action", breadcrumb.action);
    },
  },
};
</script>

<style lang="scss" scoped>
.breadcrumbs {
  margin-left: 1em;
  display: flex;
  align-items: center;
  ul {
    display: flex;
    padding-left: 0;
    font-weight: normal;
    list-style: none;
    @include media("<=tablet") {
      flex-wrap: wrap;
    }
  }
  li {
    margin: auto 0.5em auto auto;
    white-space: nowrap;
    @include media("<=tablet") {
      margin: 0;
    }
    &:not(:last-child):after {
      content: "/";
      margin-left: 0.5em;
    }
    &:last-child {
      word-break: break-all;
      white-space: pre-line;
      font-weight: 600;
      a {
        cursor: default;
        pointer-events: none;
      }
    }
  }
  &__item {
    color: var(--fg-lighter);
    text-decoration: none;
    outline: none;
    &.--action {
      cursor: pointer;
    }
  }
}
</style>
