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
  <aside
    :style="{ top: topPosition }"
    :class="['sidebar', annotationEnabled ? 'annotation' : 'explore']"
  >
    <div class="sidebar__wrapper">
      <div class="sidebar__content">
        <slot></slot>
      </div>
    </div>
  </aside>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
    topPosition() {
      return this.annotationEnabled
        ? `${this.dataset.viewSettings.headerHeight - 63}px`
        : `${this.dataset.viewSettings.headerHeight}px`;
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  top: 0;
  min-height: 300px;
  border-radius: 5px;
  width: 280px;
  position: absolute;
  right: 100px;
  background: white;
  padding: 1em 1.5em;
  overflow: auto;
  transition: top 0.2s ease-in-out;
  border: 1px solid palette(grey, smooth);
  box-shadow: 0 1px 9px 0 palette(grey, smooth);
  border-radius: 3px;
  z-index: 1;
  @include media(">desktop") {
    border-radius: 1px;
    border: none;
    box-shadow: none;
    margin-left: 1em;
    display: block !important;
    right: 100px;
  }
  &__content {
    border-radius: 2px;
    @include font-size(13px);
    &:first-child {
      padding-top: 0;
    }
  }
}
</style>
