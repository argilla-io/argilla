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
      <template v-if="datasetId && datasetName">
        <base-button
          class="header__button small"
          @on-click="onClickTrain"
          v-if="isAdminRole"
        >
          <svgicon name="code" width="20" height="20" />Train
        </base-button>
        <DatasetSettingsIcon
          :datasetId="datasetId"
          @click-settings-icon="goToSettings()"
        />
      </template>
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
import "assets/icons/code";
import { DatasetViewSettings } from "@/models/DatasetViewSettings";
import { Vector as VectorModel } from "@/models/Vector";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import {
  isExistAnyLabelsNotSavedInBackByDatasetId,
  getTotalLabelsInGlobalLabel,
} from "@/models/globalLabel.queries";
export default {
  data() {
    return {
      headerHeight: null,
    };
  },
  props: {
    datasetId: {
      type: Array,
    },
    datasetName: {
      type: String,
    },
    datasetTask: {
      type: String,
      validator(value) {
        // The value must match one of these strings
        return [
          "TextClassification",
          "TokenClassification",
          "Text2Text",
        ].includes(value);
      },
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
    dataset() {
      //TODO - when refactor of filter part from header, remove this computed/and get only what is necessary as props
      return this.datasetId && this.datasetTask
        ? getDatasetFromORM(this.datasetId, this.datasetTask, true)
        : null;
    },
    currentTaskHeader() {
      return this.datasetTask && `${this.datasetTask}Header`;
    },
    workspace() {
      return this.$route.params.workspace;
    },
    viewSettings() {
      return DatasetViewSettings.query().whereId(this.datasetName).first();
    },
    isAdminRole() {
      return this.$auth.user.role === "admin";
    },
    globalHeaderHeight() {
      if (this.sticky && this.dataset) {
        return this.viewSettings?.headerHeight;
      }
    },
    showRecordsLoader() {
      return this.viewSettings?.loading;
    },
    isReferenceRecord() {
      return VectorModel.query()
        .where("dataset_id", this.datasetId.join("."))
        .where("is_active", true)
        .exists();
    },
    datasetSettingsPageUrl() {
      if (this.datasetName) {
        const { fullPath } = this.$route;
        const datasetSettingsPageUrl = fullPath.replace("?", "/settings?");
        return datasetSettingsPageUrl;
      }
      return null;
    },
    isNoLabelInGlobalLabelModel() {
      return !getTotalLabelsInGlobalLabel(this.datasetId);
    },
    isAnyLabelsInGlobalLabelsModelNotSavedInBack() {
      return isExistAnyLabelsNotSavedInBackByDatasetId(this.datasetId);
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
        where: this.datasetName,
        data: {
          headerHeight: this.headerHeight,
        },
      });
    },
    searchRecords(query) {
      this.$emit("on-search-or-on-filter-records", query);
    },
    onClickTrain() {
      this.$emit("on-click-train");
    },
    goToSettings() {
      const currentRoute = this.$route.path;
      const newRoute = `/datasets/${this.workspace}/${this.datasetName}/settings`;
      const allowNavigate = currentRoute !== newRoute;
      if (this.datasetName && allowNavigate) {
        this.$router.push(newRoute);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
$header-button-color: #262a2e;
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

.button-settings {
  margin-right: $base-space;
  &[data-title] {
    position: relative;
    overflow: visible;
    @extend %has-tooltip--bottom;
    &:before,
    &:after {
      margin-top: calc($base-space/2);
    }
  }
}
.header__button {
  background: $header-button-color;
  color: palette(white);
  margin-right: $base-space;
  padding: 10px 12px 10px 10px;
  font-weight: 600;
  @include font-size(14px);
  box-shadow: $shadow-200;
  &:hover {
    background: darken($header-button-color, 3%);
  }
  svg {
    fill: palette(white);
  }
}
</style>
