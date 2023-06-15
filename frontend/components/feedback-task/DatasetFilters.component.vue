<template>
  <div class="filters">
    <span
      class="filters__component"
      v-for="{ id, componentType, placeholder, options } in sortedFiltersValue"
      :key="id"
    >
      <SearchBarBase
        v-if="componentType === 'searchBar'"
        v-model="searchInput"
        :placeholder="placeholder"
        :additionalInfo="additionalInfoForSearchComponent"
      />

      <StatusFilter
        v-if="componentType === 'statusSelector'"
        :options="options"
        v-model="selectedStatus"
      />
    </span>
  </div>
</template>

<script>
import { isNil } from "lodash";
import { RECORD_STATUS } from "@/models/feedback-task-model/record/record.queries";
import {
  upsertDatasetFilters,
  getFiltersByDatasetId,
} from "@/models/feedback-task-model/dataset-filter/datasetFilter.queries";

export default {
  name: "DatasetFiltersComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    orderBy: {
      type: Object,
      default: () => {
        return { orderFilterBy: "order", ascendent: true };
      },
    },
  },
  data: () => {
    return {
      selectedStatus: null,
      searchInput: null,
      sortedFiltersValue: [],
      totalRecords: null,
    };
  },
  beforeMount() {
    this.selectedStatus = this.selectedStatus || this.statusFromRoute;
    this.searchInput = this.searchInput ?? this.searchFromRoute;

    this.$root.$on("reset-status-filter", () => {
      this.selectedStatus = this.statusFromRoute;
    });
    this.$root.$on("reset-search-filter", () => {
      this.searchInput = this.searchFromRoute;
    });
    this.$root.$on("total-records", (newTotalRecords) => {
      this.totalRecords = newTotalRecords;
    });

    this.sortedFiltersValue = Object.values(this.filters).sort((a, b) =>
      a.order > b.order ? -1 : 1
    );
  },
  computed: {
    additionalInfoForSearchComponent() {
      if (isNil(this.totalRecords) || this.totalRecords === 0) return null;

      if (this.totalRecords === 1) return `${this.totalRecords} record`;
      return `${this.totalRecords} records`;
    },
    filtersFromVuex() {
      return getFiltersByDatasetId(
        this.datasetId,
        this.orderBy?.orderFilterBy,
        this.orderBy?.ascendent
      );
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
    this.filters = {
      searchText: {
        id: "searchText",
        name: "Search",
        componentType: "searchBar",
        order: 1,
        placeholder: "Introduce a query",
      },
      statusSelector: {
        id: "statusSelector",
        name: "Status Selector",
        componentType: "statusSelector",
        order: 0,
        options: [
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
        ],
      },
    };

    this.selectedStatus =
      this.$route.query?._status ?? RECORD_STATUS.PENDING.toLowerCase();
    const filterValues = Object.values(this.filters);
    const formattedFilters = this.factoryFiltersForOrm(filterValues);
    upsertDatasetFilters(formattedFilters);
  },
  methods: {
    onSearch(id, value) {
      upsertDatasetFilters({
        id,
        value,
      });
    },
    getFilterById(filterId) {
      return this.filtersFromVuex.find((filter) => filter.id === filterId);
    },
    factoryFiltersForOrm(filterValues) {
      return filterValues.map(
        ({
          id,
          name,
          componentType,
          value,
          order,
          options,
          placeholder,
          groupId,
        }) => {
          return {
            dataset_id: this.datasetId,
            id,
            name,
            order,
            component_type: componentType,
            value,
            options,
            placeholder,
            group_id: groupId,
          };
        }
      );
    },
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
  padding: $base-space * 2 0;
}
.search-area {
  width: clamp(300px, 30vw, 800px);
}
</style>
