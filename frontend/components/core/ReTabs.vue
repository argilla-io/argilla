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
  <div class="tabs">
    <div class="tabs__buttons">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['tab', { active: activeTab === tab || tabs.length === 1 }]"
        @click="changeTab(tab)"
      >
        <span>{{ tab }} </span>
      </button>
    </div>
    <slot />
  </div>
</template>
<script>
export default {
  props: ["tabs", "activeTab"],
  data: () => ({}),
  methods: {
    changeTab(tab) {
      this.$emit("change-tab", tab);
    },
  },
};
</script>
<style lang="scss" scoped>
.tabs {
  &__buttons {
    display: inline;
    position: relative;
    text-align: left;
    align-items: center;
    @include font-size(15px);
    display: flex;
  }
  &__links {
    margin-right: 0;
    margin-left: 1em;
  }
  &__button {
    margin-left: auto;
    svg {
      margin-left: 1em;
    }
  }
  &__filters {
    display: flex;
    margin-right: 0;
    margin-left: auto;
    .button--icon {
      margin-left: 0.7em;
    }
  }
}
.tab {
  padding: 0.8em 1.5em;
  font-weight: normal;
  display: inline-block;
  vertical-align: baseline;
  background: none;
  border: 0;
  outline: none;
  border-bottom: 3px solid transparent;
  transition: border-color 0.2s ease;
  color: $primary-color;
  cursor: pointer;
  &.active {
    font-weight: 700;
    border-bottom: 3px solid $primary-color;
    transition: border-color 0.4s ease;
  }
  &:hover {
    border-bottom: 3px solid $primary-color !important;
    transition: border-color 0.4s ease;
    & ~ .active {
      border-bottom: 3px solid transparent;
    }
  }
}

.button-bordered {
  @extend %button;
  text-transform: none;
  color: $primary-color;
  border: 1px solid $primary-color;
  overflow: visible;
  height: 32px;
  min-height: auto;
  line-height: 32px;
  margin-bottom: 0;
  &:hover {
    color: darken($primary-color, 5%);
    border-color: darken($primary-color, 5%);
  }
}
.button--icon {
  min-width: auto;
  width: 30px;
  height: 30px;
  padding: 0;
  text-align: center;
  display: flex;
  box-shadow: $shadow-100;
  border-radius: 2px;
  position: relative;
  transition: box-shadow 0.3s ease;
  .svg-icon {
    margin: auto;
    fill: $primary-color;
  }
  &:hover {
    box-shadow: $shadow-200;
    transition: box-shadow 0.3s ease;
  }
  &.--active {
    background: $primary-color;
    transition: $swift-ease-in-out;
    .svg-icon {
      fill: $lighter-color;
    }
  }
}
</style>
