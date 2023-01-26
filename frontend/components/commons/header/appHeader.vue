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
    <base-topbar-brand>
      <base-breadcrumbs
        :breadcrumbs="breadcrumbs"
        :copy-button="copyButton"
        @breadcrumb-action="$emit('breadcrumb-action', $event)"
      />
      <user />
    </base-topbar-brand>
    <loading-line v-if="showRecordsLoader" />
    <task-sidebar
      v-if="dataset"
      :dataset="dataset"
      @view-mode-changed="onViewModeChanged"
    />
    <component
      v-if="dataset"
      :is="currentTaskHeader"
      :datasetId="dataset.id"
      :datasetName="dataset.name"
      :datasetTask="dataset.task"
      :enableSimilaritySearch="isReferenceRecord"
      @search-records="searchRecords"
    />
  </section>
</template>

<script>
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { Vector as VectorModel } from "@/models/Vector";
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
    copyButton: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    currentTaskHeader() {
      return this.dataset.task + "Header";
    },
    viewSettings() {
      return DatasetViewSettings.query().first();
    },
    globalHeaderHeight() {
      if (this.sticky && this.dataset) {
        return this.viewSettings.headerHeight;
      }
    },
    showRecordsLoader() {
      return this.viewSettings.loading;
    },
    isReferenceRecord() {
      return VectorModel.query()
        .where("dataset_id", this.dataset.id.join("."))
        .where("is_active", true)
        .exists();
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
    onViewModeChanged(viewMode) {
      if (viewMode === "labelling-rules" && this.isReferenceRecord) {
        this.removeSimilarityFilter();
      }
    },
    removeSimilarityFilter() {
      this.searchRecords({ query: { vector: null } });
    },
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
    searchRecords(query) {
      this.$emit("on-search-or-on-filter-records", query);
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
  :deep(.header__filters) {
    position: relative;
  }
  &:not(.sticky) {
    position: relative;
  }
}
</style>
