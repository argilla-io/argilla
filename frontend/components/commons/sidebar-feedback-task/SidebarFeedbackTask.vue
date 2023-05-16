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
  <div class="sidebar" :class="expandedComponent && '--expanded'">
    <SidebarFeedbackTaskButtonGroup
      v-for="group in sidebarGroups"
      :key="group"
      :group-name="group"
      :group-button-type="getButtonType(group)"
      :groupItems="filteredSidebarItemsByGroup(group)"
      :active-buttons="activeButtons"
      @on-click-sidebar-action="onClickSidebarAction"
    />
  </div>
</template>

<script>
export default {
  props: {
    sidebarItems: {
      type: Object,
      required: true,
    },
    activeButtons: {
      type: Array,
      required: true,
    },
    expandedComponent: {
      type: String,
      default: null,
    },
  },
  computed: {
    sidebarGroups() {
      return Object.keys(this.sidebarItems);
    },
  },
  methods: {
    filteredSidebarItemsByGroup(group) {
      return this.sidebarItems[group].buttons;
    },
    getButtonType(group) {
      return this.sidebarItems[group].buttonType;
    },
    onClickSidebarAction(group, id) {
      this.$emit("on-click-sidebar-action", group, id);
    },
  },
};
</script>

<style lang="scss" scoped>
$sidebar-button-size: 45px;
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1em;
  top: 0;
  width: $sidebar-button-size;
  min-width: $sidebar-button-size;
  min-height: calc(100vh - $topbarHeight);
  min-width: $sidebarMenuWidth;
  background: palette(grey, 700);
  border-left: 1px solid $black-10;
  box-shadow: none;
  pointer-events: all;
  transition: box-shadow 0.2s ease-in-out 0.4s;
  // TODO - Only for MVP
  padding-top: $base-space * 2;
  &.--expanded {
    box-shadow: inset 1px 1px 5px -2px #c7c7c7;
    transition: box-shadow 0.2s ease-in-out;
  }
  p {
    text-align: center;
    font-weight: 600;
    @include font-size(12px);
    margin-bottom: 0.5em;
  }
  a {
    position: relative;
    display: block;
    outline: none;
  }
  &__info {
    position: relative;
  }
}
</style>
