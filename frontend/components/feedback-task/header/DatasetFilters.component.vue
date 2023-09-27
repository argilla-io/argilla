<template>
  <div class="filters">
    <SearchBarBase
      v-model="searchInput"
      :placeholder="'Introduce a query'"
      :additionalInfo="additionalInfoForSearchComponent"
    />
    <MetadataFilter :datasetId="datasetId" />
    <StatusFilter
      class="filters__status"
      :options="statusOptions"
      v-model="selectedStatus"
    />
  </div>
</template>

<script>
export default {
  name: "DatasetFiltersComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data: () => {
    return {
      selectedStatus: null,
      searchInput: null,
      totalRecords: null,
    };
  },
  beforeMount() {
    this.selectedStatus = this.selectedStatus ?? this.statusFromRoute;
    this.searchInput = this.searchInput ?? this.searchFromRoute;

    this.$root.$on("reset-status-filter", () => {
      this.selectedStatus = this.statusFromRoute;
    });
    this.$root.$on("reset-search-filter", () => {
      this.searchInput = this.searchFromRoute;
    });
    this.$root.$on("total-records", (totalRecords) => {
      this.totalRecords = totalRecords;
    });
  },
  computed: {
    additionalInfoForSearchComponent() {
      if (!this.totalRecords || this.totalRecords === 0) return null;

      if (this.totalRecords === 1) return `${this.totalRecords} record`;
      return `${this.totalRecords} records`;
    },
    statusFromRoute() {
      return this.$route.query?._status;
    },
    searchFromRoute() {
      return this.$route.query?._search;
    },
  },
  watch: {
    selectedStatus(newValue) {
      this.$root.$emit("status-filter-changed", newValue);
    },
    searchInput(searchInput) {
      this.$root.$emit("search-filter-changed", searchInput);
    },
  },
  created() {
    this.statusOptions = [
      {
        id: "pending",
        name: "Pending",
      },
      {
        id: "submitted",
        name: "Submitted",
      },
      {
        id: "discarded",
        name: "Discarded",
      },
    ];
  },
  beforeDestroy() {
    this.$root.$off("reset-status-filter");
    this.$root.$off("reset-search-filter");
    this.$root.$off("total-records");
  },
};
</script>

<style lang="scss" scoped>
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: $base-space * 2;
  align-items: center;
  width: 100%;
  padding: $base-space * 2 0;
  &__status {
    margin-left: auto;
  }
}
.search-area {
  width: clamp(300px, 30vw, 800px);
}
</style>
