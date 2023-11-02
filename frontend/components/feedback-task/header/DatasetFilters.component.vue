<template>
  <div class="filters__wrapper">
    <div class="filters">
      <SearchBarBase
        v-model="recordCriteria.searchText"
        :placeholder="'Introduce a query'"
      />
      <FilterButton
        v-if="isAnyAvailableFilter"
        @click.native="toggleVisibilityOfFilters"
        :button-name="$t('filters')"
        :show-chevron-icon="false"
        :is-button-active="isAnyFilterActive"
      />
      <Sort
        v-if="!!datasetMetadata.length"
        :datasetMetadata="datasetMetadata"
        v-model="recordCriteria.sortBy"
      />
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

      if (this.totalRecords === 1) return `${this.totalRecords} record`;

      return `${this.totalRecords} records`;
    },
    shouldShowTotalRecords() {
      return (
        this.recordCriteria.isFilteredByText ||
        this.recordCriteria.isFilteredByMetadata
      );
    },
    isAnyAvailableFilter() {
      return !!this.datasetMetadata.length;
    },
    isAnyFilterActive() {
      return this.recordCriteria.isFilteredByMetadata;
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
  },
  destroyed() {
    this.$root.$off("on-changed-total-records");
  },
};
</script>

<style lang="scss" scoped>
.filters {
  display: flex;
  flex-wrap: nowrap;
  gap: $base-space;
  align-items: center;
  &__wrapper {
    width: 100%;
    padding: $base-space * 2 $base-space * 3;
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
</style>
