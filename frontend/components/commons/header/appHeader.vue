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
  <section
    id="header"
    ref="header"
    :class="['header', sticky && dataset ? 'sticky' : null]"
  >
    <ReTopbarBrand>
      <ReBreadcrumbs :breadcrumbs="breadcrumbs" :copy-button="true" />
      <user />
    </ReTopbarBrand>
    <slot />
    <component v-if="dataset" :is="currentTaskHeader" :dataset="dataset" />
  </section>
</template>

<script>
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
export default {
  data: () => {
    return {
      headerHeight: undefined,
    };
  },
  props: {
    dataset: {
      type: Object,
    },
    breadcrumbs: {
      type: Array,
    },
    sticky: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    currentTask() {
      return this.dataset.task;
    },
    currentTaskHeader() {
      return this.currentTask + "Header";
    },
    globalHeaderHeight() {
      if (this.sticky && this.dataset) {
        return this.dataset.viewSettings.headerHeight;
      }
    },
  },
  mounted() {
    if (this.sticky && this.dataset) {
      this.setHeaderHeight();
    }
  },
  watch: {
    globalHeaderHeight() {
      if (this.dataset && this.globalHeaderHeight !== this.headerHeight) {
        this.headerHeightUpdate();
      }
    },
  },
  methods: {
    async setHeaderHeight() {
      const header = this.$refs.header;
      const resize_ob = new ResizeObserver(() => {
        this.headerHeight = header.offsetHeight;
        this.headerHeightUpdate();
      });
      resize_ob.observe(header);
    },
    headerHeightUpdate() {
      DatasetViewSettings.update({
        where: this.dataset.name,
        data: {
          headerHeight: this.headerHeight,
        },
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.header {
  opacity: 1;
  position: relative;
  transition: none;
  top: 0;
  right: 0;
  left: 0;
  transform: translateY(0);
  position: sticky;
  background: $bg;
  z-index: 3;
  ::v-deep .header__filters {
    position: relative;
  }
  &:not(.sticky) {
    position: relative;
  }
}
</style>
