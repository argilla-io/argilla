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
      return this.dataset.viewSettings.annotationEnabled;
    },
    topPosition() {
      return this.annotationEnabled
        ? `${this.dataset.viewSettings.headerHeight - 60}px`
        : `${this.dataset.viewSettings.headerHeight + 10}px`;
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  min-height: 300px;
  border-radius: 5px;
  width: 280px;
  position: absolute;
  right: 3.5em;
  background: white;
  padding: 1em 2em;
  box-shadow: 0 5px 11px 0 rgba(0, 0, 0, 0.5);
  overflow: auto;
  transition: top 0.2s ease-in-out;
  z-index: 2;
  @include media(">desktopLarge") {
    margin-left: 1em;
    display: block !important;
    right: calc(4em + 45px);
  }
  .fixed-header .--annotation & {
    margin-top: 70px;
  }
  &__content {
    border-radius: 2px;
    @include font-size(13px);
    &:first-child {
      padding-top: 0;
    }
    p {
      display: flex;
      align-items: flex-end;
      @include font-size(18px);
      margin-top: 0;
      margin-bottom: 2em;
      font-weight: 600;
      svg {
        margin-right: 1em;
      }
    }
  }
}
</style>
