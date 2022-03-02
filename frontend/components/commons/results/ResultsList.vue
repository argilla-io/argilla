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
            <results-empty
              :title="emptySearchInfo.title"
              :message="emptySearchInfo.message"
              :icon="emptySearchInfo.icon"
              v-else-if="dataset.results.total === 0"
            />
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
                @show-metadata="onShowMetadata"
                :key="`${dataset.name}-${item.id}`"
                :dataset="dataset"
                :item="item"
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
      <RePagination
        :total-items="dataset.results.total"
        :pagination-settings="dataset.viewSettings.pagination"
        @changePage="onPagination"
      />
    </div>
    <LazyReModal
      modal-class="modal-secondary"
      modal-position="modal-center"
      :modal-custom="true"
      :prevent-body-scroll="true"
      :modal-visible="selectedRecord !== undefined"
      @close-modal="onCloseMetadata"
    >
      <Metadata
        v-if="selectedRecord"
        :applied-filters="dataset.query.metadata"
        :metadata-items="selectedRecord.metadata"
        :title="selectedRecord.recordTitle()"
        @metafilterApply="onApplyMetadataFilter"
        @cancel="onCloseMetadata"
      />
    </LazyReModal>
  </span>
</template>
<script>
import "assets/icons/empty-results";
import { mapActions } from "vuex";
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
      emptySearchInfo: {
        // message: "There is no result. <br />Try another query.",
        icon: "empty-results",
      },
    };
  },
  computed: {
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
      this.search({
        dataset: this.dataset,
        query: { metadata: metadata },
      });
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
  },
};
</script>
<style lang="scss" scoped>
.content {
  $this: &;
  padding: 0;
  width: 100%;
  position: relative;
  margin-bottom: 0;
  list-style: none;
  padding-right: calc(4em + 45px);
  z-index: 0;
  .--metrics & {
    @include media(">desktop") {
      width: 100%;
      padding-right: calc(294px + 100px);
      transition: padding 0.1s ease-in-out;
    }
  }
  @include media(">desktop") {
    transition: padding 0.1s ease-in-out;
    width: 100%;
    padding-right: 100px;
  }
  .results-scroll {
    height: 100vh !important;
    overflow: auto;
    padding-left: 4em;
    padding-bottom: 260px;
    transition: padding 0s ease-in-out 0.1s;
    &::-webkit-scrollbar {
      display: none;
    }
  }
  &__li {
    margin-bottom: -1px;
    position: relative;
    min-height: 80px;
  }
}
</style>

<style lang="scss">
.vue-recycle-scroller__item-wrapper {
  box-sizing: content-box;
  padding-bottom: 260px;

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
