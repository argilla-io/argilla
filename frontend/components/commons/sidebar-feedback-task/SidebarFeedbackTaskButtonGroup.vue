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
  <span class="sidebar__info">
    <!-- NOTE: HIDDEN FOR MVP
    <p class="sidebar__info__title" v-text="groupName"></p> -->
    <IconButton
      v-for="{ id, icon, tooltip } in groupItems"
      :id="id"
      :key="id"
      :icon="icon"
      :tooltip="tooltip"
      :button-type="groupButtonType"
      :is-button-active="checkIfButtonIsActive(id)"
      @on-button-action="onAction(id)"
    />
  </span>
</template>

<script>
export default {
  props: {
    groupItems: {
      type: Array,
      required: true,
    },
    groupName: {
      type: String,
      required: true,
    },
    groupButtonType: {
      type: String,
      required: true,
    },
    activeButtons: {
      type: Array,
      required: true,
    },
  },
  methods: {
    checkIfButtonIsActive(id) {
      return this.activeButtons.includes(id);
    },
    onAction(id) {
      this.$emit("on-click-sidebar-action", this.groupName, id);
    },
  },
};
</script>

<style lang="scss" scoped>
.sidebar {
  &__info {
    position: relative;
    &__title {
      margin-bottom: 0.5em;
      text-align: center;
      font-weight: 600;
      @include font-size(12px);
      text-transform: capitalize;
    }
  }
}
</style>
