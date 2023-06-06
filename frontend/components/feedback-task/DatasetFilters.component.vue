<template>
  <div class="filters">
    <span
      class="filters__component"
      v-for="filterObj in sortedFiltersValue"
      :key="filterObj.id"
    >
      <SearchBarBase
        v-if="filterObj.componentType === 'searchBar'"
        :placeholder="filterObj.placeholder"
        v-model="searchInput"
      />

      <StatusFilter
        v-if="filterObj.componentType === 'statusSelector'"
        :options="filterObj.options"
        v-model="selectedStatus"
      />
    </span>
  </div>
</template>

<script>
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

    this.sortedFiltersValue = Object.values(this.filters).sort((a, b) =>
      a.order > b.order ? -1 : 1
    );
  },
  computed: {
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
    async searchInput(searchInput) {
      this.$root.$emit("search-filter-changed", searchInput);
    },
  },
  created() {
    this.filters = {
      searchText: {
        id: "searchText",
        name: "Search",
        componentType: "searchBar",
        order: 0,
        placeholder: "Introduce your query",
      },
      statusSelector: {
        id: "statusSelector",
        name: "Status Selector",
        componentType: "statusSelector",
        order: 1,
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
</style>
