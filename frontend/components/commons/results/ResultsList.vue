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
  <div v-if="dataset">
    <div class="content">
      <slot name="header" />
      <div class="results-scroll" id="scroll">
        <DynamicScroller
          page-mode
          class="scroller"
          :items="visibleRecords"
          :min-item-size="550"
          :buffer="200"
          :key="showLoader"
        >
          <template #before>
            <slot name="results-header" />
            <similarity-record-reference-component
              v-if="referenceRecordObj && !showLoader"
              :datasetId="datasetId"
              :datasetTask="datasetTask"
              :referenceRecord="referenceRecordObj"
              @search-records="searchRecords"
              @show-record-info-modal="onShowRecordInfoModal"
            />
            <results-loading
              v-if="showLoader"
              :size="viewSettings.pagination.size"
            />
            <results-empty v-else-if="dataset.results.total === 0" />
          </template>

          <template v-slot="{ item, index, active }">
            <DynamicScrollerItem
              v-show="!showLoader && dataset.results.total > 0"
              :watch-data="true"
              class="content__li"
              :item="item"
              :active="active"
              key-field="id"
              :index="index"
              :data-index="index"
            >
              <results-record
                :key="`${dataset.name}-${item.id}`"
                :datasetId="datasetId"
                :datasetTask="dataset.task"
                :record="item"
                @show-record-info-modal="onShowRecordInfoModal"
                @search-records="searchRecords"
              />
            </DynamicScrollerItem>
          </template>

          <template #after>
            <pagination-end-alert
              :limit="paginationLimit"
              v-if="isLastPagePaginable"
            />
          </template>
        </DynamicScroller>
      </div>
      <base-pagination
        v-if="!showLoader"
        :one-page="!!referenceRecordObj"
        :total-items="dataset.results.total"
        :pagination-settings="viewSettings.pagination"
        @changePage="onPagination"
      />
    </div>
    <lazy-base-modal
      modal-class="modal-table"
      :modal-custom="true"
      :prevent-body-scroll="true"
      modal-title="Record info"
      :modal-visible="selectedRecord !== undefined"
      @close-modal="onCloseRecordInfo"
    >
      <record-info
        v-if="selectedRecord"
        :record="selectedRecord"
        @close-modal="onCloseRecordInfo"
      />
    </lazy-base-modal>
  </div>
</template>

<script>
import "assets/icons/smile-sad";
import { mapActions } from "vuex";
import { Vector as VectorModel } from "@/models/Vector";
import { RefRecord as RefRecordModel } from "@/models/RefRecord";
import { getDatasetFromORM } from "@/models/dataset.utilities";
import { getViewSettingsWithPaginationByDatasetName } from "@/models/viewSettings.queries";

export default {
  name: "ResultsList",
  props: {
    datasetId: {
      type: Array,
      required: true,
    },
    datasetTask: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      scrollComponent: undefined,
      selectedRecord: undefined,
      test: null,
    };
  },
  computed: {
    dataset() {
      return getDatasetFromORM(this.datasetId, this.datasetTask);
    },
    viewSettings() {
      return this.dataset.name
        ? getViewSettingsWithPaginationByDatasetName(this.dataset.name)
        : {};
    },
    referenceRecordId() {
      return VectorModel.query()
        .where("is_active", true)
        .where("dataset_id", this.dataset.id.join("."))
        .first()?.record_id;
    },
    referenceRecordObj() {
      return RefRecordModel.query()
        .where("record_id", this.referenceRecordId)
        .first()?.record_object;
    },
    showLoader() {
      return this.viewSettings.loading;
    },
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    paginationLimit() {
      return this.viewSettings.pagination.maxRecordsLimit;
    },
    isLastPagePaginable() {
      if (this.dataset.results.total > this.paginationLimit) {
        return (
          this.viewSettings.pagination.page *
            this.viewSettings.pagination.size ===
          this.viewSettings.pagination.maxRecordsLimit
        );
      }
      return false;
    },
  },
  methods: {
    ...mapActions({
      paginate: "entities/datasets/paginate",
      search: "entities/datasets/search",
    }),
    onShowRecordInfoModal(record) {
      this.selectedRecord = record;
    },
    onCloseRecordInfo() {
      this.selectedRecord = undefined;
    },
    async onPagination(page, size) {
      await this.paginate({
        dataset: this.dataset,
        page: page,
        size: size,
      });
    },
    searchRecords(query) {
      this.$emit("search-records", query);
    },
  },
};
</script>

<style lang="scss" scoped>
.content {
  $this: &;
  width: 100%;
  position: relative;
  margin-bottom: 0;
  list-style: none;
  z-index: 0;
  @extend %collapsable-if-metrics !optional;
  .results-scroll {
    height: 100vh !important;
    overflow: auto;
    padding-left: 4em;
    padding-bottom: 260px;
    transition: padding 0s ease-in-out 0.1s;
    @extend %hide-scrollbar;
  }
  &__li {
    position: relative;
    min-height: 80px;
  }
}
</style>

<style lang="scss">
.vue-recycle-scroller__item-wrapper {
  box-sizing: content-box;
  z-index: 0;
}

.vue-recycle-scroller__item-view {
  box-sizing: border-box;
}

$maxItemsperPage: 20;
@for $i from 0 through $maxItemsperPage {
  .vue-recycle-scroller__item-view:nth-of-type(#{$i}) {
    z-index: $maxItemsperPage - $i;
  }
}
</style>
