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
  <div v-if="annotationEnabled" class="container">
    <div class="global-actions">
      <slot />
    </div>
  </div>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({}),
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.viewMode === "annotate";
    },
  },
};
</script>
<style lang="scss" scoped>
.container {
  @extend %container;
  margin: 0 auto auto 0;
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 4em;
  padding-right: calc(4em + 45px);
  .--metrics & {
    @include media(">desktop") {
      padding-right: calc(294px + 100px);
      transition: padding 0.1s ease-in-out;
    }
  }
  @include media(">desktop") {
    transition: padding 0.1s ease-in-out;
    width: 100%;
    padding-right: 100px;
  }
}
.global-actions {
  display: flex;
  align-items: center;
  width: 100%;
  text-align: left;
  padding: 1em 1.4em;
  background: $lighter-color;
  border-radius: 3px 3px 1px 1px;
  border: 1px solid palette(grey, smooth);
  position: relative;
  margin-bottom: -1px;
  &--exploration {
    position: relative;
  }
}
</style>
