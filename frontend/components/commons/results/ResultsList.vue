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
  <div class="list">
    <slot name="header" />
    <VueAutoVirtualScrollList
      id="scroll"
      ref="scroll"
      :key="dataset.name"
      class="results-scroll"
      :total-height="1200"
      :default-height="100"
      :style="{ paddingTop: `${dataset.viewSettings.headerHeight + 10}px` }"
    >
      <template v-if="showLoader">
        <results-loading :size="dataset.viewSettings.pagination.size" />
      </template>
      <template v-else>
        <div
          v-for="(item, index) in visibleRecords"
          v-cloak
          :key="index"
          class="list__li"
        >
          <results-record v-if="item" :dataset="dataset" :item="item">
            <slot name="record" :record="item" />
          </results-record>
        </div>
        <pagination-end-alert :limit="paginationLimit" v-if="isLastPagePaginable" />
      </template>
    </VueAutoVirtualScrollList>
    <RePagination
      :total-items="dataset.results.total"
      :pagination-settings="dataset.viewSettings.pagination"
      @changePage="onPagination"
    />
  </div>
</template>
<script>
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
        return (this.dataset.viewSettings.pagination.page * this.dataset.viewSettings.pagination.size) === this.dataset.viewSettings.pagination.maxRecordsLimit;
      }
      return false
    }
  },
  mounted() {
    const scroll = document.getElementById("scroll");
    if (scroll) {
      this.scrollComponent = scroll;
      this.scrollComponent.addEventListener("scroll", this.onScroll);
    }
  },
  beforeDestroy() {
    if (this.scrollComponent)
      this.scrollComponent.removeEventListener("scroll", this.onScroll);
  },
  methods: {
    ...mapActions({
      paginate: "entities/datasets/paginate",
    }),
    onScroll() {
      if (this.$refs.scroll.scrollTop > 0) {
        document.getElementsByTagName("body")[0].classList.add("fixed-header");
      } else {
        document
          .getElementsByTagName("body")[0]
          .classList.remove("fixed-header");

      }
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
.list {
  $this: &;
  padding: 0;
  width: 100%;
  position: relative;
  margin-bottom: 0;
  list-style: none;
  .results-scroll {
    height: 100vh !important;
    overflow: auto;
    padding-left: 4em;
    padding-bottom: 61px;
    padding-right: calc(4em + 45px);
    transition: padding 0s ease-in-out 0.1s;
    .fixed-header & {
      padding-bottom: 200px;
    }
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
  }
  &__li {
    padding-bottom: 10px;
    position: relative;
  }
}
</style>
