<template>
  <div class="filters__wrapper">
    <div class="filters">
      <SearchBarBase
        v-model="recordCriteria.searchText"
        :placeholder="'Introduce a query'"
      />
      <FilterButton
        v-if="isAnyAvailableFilter"
        class="filters__filter-button"
        @click.native="toggleVisibilityOfFilters"
        :button-name="$t('filters')"
        icon-name="filter"
        :show-chevron-icon="false"
        :is-button-active="isAnyFilterActive"
      />
      <Sort
        v-if="!!datasetMetadata.length"
        :datasetMetadata="datasetMetadata"
        v-model="recordCriteria.sortBy"
      />
      <BaseButton
        v-if="isAnyFilterActive || isSortedBy"
        class="small clear filters__reset-button"
        @on-click="resetFiltersAndSortBy()"
        >{{ $t("reset") }}</BaseButton
      >
      <p v-if="shouldShowTotalRecords" class="filters__total-records">
        {{ totalRecordsInfo }}
      </p>
      <StatusFilter class="filters__status" v-model="recordCriteria.status" />
    </div>
    <transition name="filterAppear" v-if="visibleFilters" appear>
      <div class="filters__list">
        <MetadataFilter
          v-if="!!datasetMetadata.length"
          :datasetMetadata="datasetMetadata"
          v-model="recordCriteria.metadata"
        />
        <ResponsesFilter
          v-if="!!datasetQuestions.length"
          :datasetQuestions="datasetQuestions"
          v-model="recordCriteria.metadata"
        />
        <SuggestionFilter :datasetQuestions="datasetQuestions" />
      </div>
    </transition>
  </div>
</template>

<script>
import { useDatasetsFiltersViewModel } from "./useDatasetsFiltersViewModel";

export default {
  name: "DatasetFiltersComponent",
  props: {
    recordCriteria: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {
      totalRecords: null,
      visibleFilters: false,
    };
  },
  computed: {
    totalRecordsInfo() {
      if (!this.totalRecords || this.totalRecords === 0) return null;

      return this.totalRecords;
    },
    shouldShowTotalRecords() {
      return (
        this.recordCriteria.isFilteredByText ||
        this.recordCriteria.isFilteredByMetadata
      );
    },
    isAnyAvailableFilter() {
      return !!this.datasetMetadata.length || !!this.datasetQuestions.length;
    },
    isAnyFilterActive() {
      return this.recordCriteria.isFilteredByMetadata;
    },
    isSortedBy() {
      return this.recordCriteria.isSortedBy;
    },
  },
  methods: {
    newFiltersChanged() {
      if (!this.recordCriteria.hasChanges) return;
      if (!this.recordCriteria.isChangingAutomatically) {
        this.recordCriteria.page = 1;
      }

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
    },
    toggleVisibilityOfFilters() {
      this.visibleFilters = !this.visibleFilters;
    },
    resetFiltersAndSortBy() {
      this.recordCriteria.resetFiltersAndSortBy();
    },
  },
  watch: {
    "recordCriteria.searchText"() {
      this.newFiltersChanged();
    },
    "recordCriteria.status"() {
      this.newFiltersChanged();
    },
    "recordCriteria.metadata"() {
      this.newFiltersChanged();
    },
    "recordCriteria.sortBy"() {
      this.newFiltersChanged();
    },
  },
  setup() {
    return useDatasetsFiltersViewModel();
  },
  mounted() {
    this.$root.$on("on-changed-total-records", (totalRecords) => {
      this.totalRecords = totalRecords;
    });

    this.loadMetadata(this.recordCriteria.datasetId);
    this.loadQuestions(this.recordCriteria.datasetId);
  },
  destroyed() {
    this.$root.$off("on-changed-total-records");
  },
};
</script>

<style lang="scss" scoped>
$filters-inline-min-width: 540px;
.filters {
  display: flex;
  gap: $base-space;
  align-items: center;
  &__wrapper {
    width: 100%;
    container-type: inline-size;
    container-name: filters;
    z-index: 1;
  }
  &__list {
    display: flex;
    gap: $base-space;
    width: 100%;
    padding-top: $base-space;
  }
  &__total-records {
    flex-shrink: 0;
    margin: 0;
    @include font-size(13px);
    color: $black-37;
  }
  &__status {
    margin-left: auto;
  }
  &__reset-button {
    @include font-size(13px);
    flex-shrink: 0;
  }
  &__filter-button {
    &.filter-button--active {
      background: none;
      &,
      :deep(.button) {
        color: palette(purple, 200);
      }
      &:hover {
        background: palette(purple, 400);
      }
    }
  }
  .search-area {
    width: min(100%, 400px);
  }
}

.filterAppear-enter-active,
.filterAppear-leave-active {
  transition: all 0.3s ease-out;
}

.filterAppear-enter,
.filterAppear-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@container filters (max-width: #{$filters-inline-min-width}) {
  .filters {
    flex-wrap: wrap;
  }
}
</style>
