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
  <span>
    <div class="content">
      <slot name="header" />
      <div class="results-scroll" id="scroll">
        <DynamicScroller
          page-mode
          class="scroller"
          :items="visibleRecords"
          :min-item-size="550"
          :buffer="200"
        >
          <template #before>
            <slot name="results-header" />
            <results-loading
              v-if="showLoader"
              :size="dataset.viewSettings.pagination.size"
            />
            <results-empty v-else-if="dataset.results.total === 0" />
            <similarity-record-reference-component
              v-if="referenceRecordObj && !showLoader"
              :dataset="dataset"
              :referenceRecord="referenceRecordObj"
              @search-records="searchRecords"
              @show-metadata="onShowMetadata"
            >
              <slot name="record" :record="referenceRecordObj" />
            </similarity-record-reference-component>
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
                :dataset="dataset"
                :item="item"
                @search-records="searchRecords"
                @show-metadata="onShowMetadata"
              >
                <slot name="record" :record="item" />
              </results-record>
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
        v-if="!referenceRecordObj"
        :total-items="dataset.results.total"
        :pagination-settings="dataset.viewSettings.pagination"
        @changePage="onPagination"
      />
    </div>
    <lazy-base-modal
      modal-class="modal-secondary"
      :modal-custom="true"
      :prevent-body-scroll="true"
      :modal-visible="selectedRecord !== undefined"
      @close-modal="onCloseMetadata"
    >
      <metadata
        v-if="selectedRecord"
        :applied-filters="dataset.query.metadata"
        :metadata-items="selectedRecord.metadata"
        :title="selectedRecord.recordTitle()"
        @metafilterApply="onApplyMetadataFilter"
        @cancel="onCloseMetadata"
      />
    </lazy-base-modal>
  </span>
</template>

<script>
import "assets/icons/smile-sad";
import { mapActions } from "vuex";
import { Vector as VectorModel } from "@/models/Vector";
import { RefRecord as RefRecordModel } from "@/models/RefRecord";

export default {
  props: {
    dataset: {
      type: Object,
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
    referenceRecordId() {
      return (
        VectorModel.query()
          .where("is_active", true)
          .where("dataset_id", this.dataset.id.join("."))
          .first()?.record_id || null
      );
    },
    referenceRecordObj() {
      const found =
        this.referenceRecordId &&
        RefRecordModel.query()
          .where("record_id", this.referenceRecordId)
          .first();

      return found?.record_object;
    },
    showLoader() {
      return this.dataset.viewSettings.loading;
    },
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    paginationLimit() {
      return this.dataset.viewSettings.pagination.maxRecordsLimit;
    },
    isLastPagePaginable() {
      if (this.dataset.results.total > this.paginationLimit) {
        return (
          this.dataset.viewSettings.pagination.page *
            this.dataset.viewSettings.pagination.size ===
          this.dataset.viewSettings.pagination.maxRecordsLimit
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
    async onApplyMetadataFilter(metadata) {
      this.onCloseMetadata();
      this.searchRecords({ query: { metadata: metadata } });
    },
    onShowMetadata(record) {
      this.selectedRecord = record;
    },
    onCloseMetadata() {
      this.selectedRecord = undefined;
    },
    async onPagination(page, size) {
      document.getElementById("scroll").scrollTop = 0;
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
