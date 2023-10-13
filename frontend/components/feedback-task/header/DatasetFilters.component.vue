<template>
  <div class="filters">
    <SearchBarBase
      v-model="recordCriteria.searchText"
      :placeholder="'Introduce a query'"
    />
    <MetadataFilter
      v-if="!!datasetMetadata.length"
      :datasetMetadata="datasetMetadata"
      v-model="recordCriteria.metadata"
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
        this.recordCriteria.isFilteringByText ||
        this.recordCriteria.isFilteringByMetadata
      );
    },
  },
  methods: {
    newFiltersChanged() {
      if (!this.recordCriteria.hasChanges) return;

      this.$root.$emit("on-change-record-criteria-filter", this.recordCriteria);
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
  created() {
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
  gap: $base-space * 2;
  align-items: center;
  width: 100%;
  padding: $base-space * 2 0;
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
</style>
