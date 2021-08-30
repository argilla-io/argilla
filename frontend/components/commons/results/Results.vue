<template>
  <ResultsEmpty
    v-if="dataset.results.total === 0"
    empty-title="0 results found"
  />
  <div v-else ref="resultsList" class="results">
    <div class="list">
      <ExplainHelpInfo v-if="isExplainedRecord"></ExplainHelpInfo>
      <VueAutoVirtualScrollList
        id="scroll"
        :key="dataset.task"
        ref="scroll"
        style="width: 100%"
        class="virtual-scroll"
        :total-height="1200"
        :default-height="100"
      >
        <div
          v-for="(item, index) in visibleRecords"
          :key="index"
          class="list__li"
        >
          <div
            :class="
              annotationEnabled ? 'list__item--annotation-mode' : 'list__item'
            "
          >
            <div
              v-if="annotationEnabled && item.status !== 'Default'"
              class="list__li__status"
            >
              {{ item.status }}
            </div>
            <ReCheckbox
              v-if="annotationEnabled"
              class="list__checkbox"
              :value="item.selected"
              @change="onCheckboxChanged($event, item.id)"
            ></ReCheckbox>
            <RecordTokenClassification
              v-if="dataset.task === 'TokenClassification'"
              :dataset="dataset"
              :record="item"
              @onShowMetadata="onShowMetadata(item.id)"
            />
            <RecordTextClassification
              v-if="dataset.task === 'TextClassification'"
              :dataset="dataset"
              :record="item"
              @onShowMetadata="onShowMetadata(item.id)"
            />
          </div>
          <LazyReModal
            :modal-custom="true"
            :prevent-body-scroll="true"
            modal-class="modal-secondary"
            :modal-visible="showMetadata === item.id"
            modal-position="modal-center"
            @close-modal="onCloseModal"
          >
            <Metadata
              :applied-filters="dataset.query.metadata"
              :metadata-items="item.metadata"
              :inputs="item.inputs"
              @metafilterApply="onMetaFilterApply"
              @cancel="onCloseModal"
            />
          </LazyReModal>
        </div>
        <ReShowMoreData
          v-if="moreDataAvailable"
          :items="visibleRecords.length"
          :total="dataset.results.total"
          :more-data-size="dataset.viewSettings.pagination.size"
          @moredata="onShowMoreData"
        />
      </VueAutoVirtualScrollList>
    </div>
  </div>
</template>

<script>
import "assets/icons/check";
import "assets/icons/help";

import { mapActions } from "vuex";

export default {
  props: {
    dataset: {
      type: Object,
      default: () => ({}),
    },
  },
  data: () => ({
    showMetadata: undefined,
    isSelectedRecord: false,
    scrollComponent: undefined,
  }),
  computed: {
    visibleRecords() {
      return this.dataset.visibleRecords;
    },
    currentQuery() {
      return this.dataset.query;
    },
    results() {
      return this.dataset.results;
    },
    moreDataAvailable() {
      return this.visibleRecords.length < this.results.total;
    },
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
    isExplainedRecord() {
      return this.dataset.results.records.some((record) => record.explanation);
    },
  },

  // TODO (@leireaguirrework): All scroll logic will be moved to layout component
  mounted() {
    const scroll = document.getElementById("scroll");
    if (scroll) {
      this.scrollComponent = scroll;
      this.scrollComponent.addEventListener("scroll", this.onScroll);
    }
  },
  // TODO (@leireaguirrework): All scroll logic will be moved to layout component
  beforeDestroy() {
    if (this.scrollComponent)
      this.scrollComponent.removeEventListener("scroll", this.onScroll);
  },
  methods: {
    ...mapActions({
      fetchMoreRecords: "entities/datasets/fetchMoreRecords",
      resetPagination: "entities/datasets/resetPagination",
      updateRecords: "entities/datasets/updateRecords",
      search: "entities/datasets/search",
    }),
    async onShowMoreData() {
      this.fetchMoreRecords({
        dataset: this.dataset,
      });
    },
    onMetaFilterApply(metadata) {
      this.onCloseModal();
      this.search({
        dataset: this.dataset,
        query: { metadata: metadata },
      });
    },
    onShowMetadata(id) {
      this.showMetadata = id;
    },
    onCheckboxChanged(selected, id) {
      const record = this.visibleRecords.find((r) => r.id === id);
      this.updateRecords({
        dataset: this.dataset,
        records: [{ ...record, selected }],
      });
    },
    onCloseModal() {
      this.showMetadata = false;
    },
    // TODO (@leireaguirrework): All scroll logic will be moved to layout component
    onScroll() {
      if (this.$refs.scroll.scrollTop > 100) {
        document.getElementsByTagName("body")[0].classList.add("fixed-header");
      } else {
        document
          .getElementsByTagName("body")[0]
          .classList.remove("fixed-header");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.results {
  flex-grow: 2;
}

.show-record-number {
  position: fixed;
  overflow: scroll;
  top: 7em;
  right: 1em;
  background: $lighter-color;
  border-radius: 10px;
  min-height: 30px;
  line-height: 30px;
  padding: 0 0.5em;
  display: none;
  span {
    @include font-size(20px);
    margin-right: 10px;
    color: $line-smooth-color;
  }
  .fixed-header & {
    display: block;
  }
}

.list {
  $this: &;
  padding: 0;
  width: 100%;
  position: relative;
  margin-bottom: 0;
  list-style: none;
  .virtual-scroll {
    padding-top: 1em;
    height: 100vh !important;
  }
  &__checkbox.re-checkbox {
    position: absolute;
    left: 1.2em;
    top: 1.2em;
    width: auto;
  }
  &__li {
    &__status {
      position: absolute;
      top: 1em;
      right: 1em;
      font-style: italic;
    }
    padding-bottom: 2px;
    position: relative;
    &.--discarded {
      ::v-deep .record,
      ::v-deep .feedback-interactions {
        opacity: 0.3;
        pointer-events: none;
      }
    }
  }
  &__item {
    position: relative;
    background: $lighter-color;
    border-radius: 3px;
    &__asterisk {
      @include font-size(24px);
      color: $secondary-color;
    }
  }
}

.list__item {
  // padding-left: 3em;
  // padding-right: 3em;
  // padding-bottom: 1em;
  // margin-left: 0;
  // padding-top: 2.2em;
  &--annotation-mode {
    // padding-left: 4em;
    @extend .list__item;
  }
  &__checkbox.re-checkbox {
    position: absolute;
    left: 1.2em;
    top: 1.2em;
    width: auto;
  }
}

.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
