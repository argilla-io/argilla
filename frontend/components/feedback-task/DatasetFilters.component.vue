<template>
  <div class="filters">
    <span
      class="filters__component"
      v-for="{ id } in sortedFiltersValue"
      :key="id"
    >
      <SearchBarBase
        v-if="getFilterById(id).component_type === 'searchBar'"
        :current-search-text="getFilterById(id).value"
        @on-search-text="onSearch(id, $event)"
        :placeholder="getFilterById(id).placeholder"
      />
      <StatusFilter
        v-if="getFilterById(id).component_type === 'statusSelector'"
        :options="getFilterById(id).options"
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
    };
  },
  mounted() {
    this.selectedStatus = this.selectedStatus || this.statusFromRoute;

    this.$root.$on("reset-status-filter", () => {
      this.selectedStatus = this.statusFromRoute;
    });
  },

  computed: {
    filtersFromVuex() {
      return getFiltersByDatasetId(
        this.datasetId,
        this.orderBy?.orderFilterBy,
        this.orderBy?.ascendent
      );
    },
    sortedFiltersValue() {
      return Object.values(this.filters).sort((a, b) =>
        a.order > b.order ? -1 : 1
      );
    },
    statusFromRoute() {
      return this.$route.query?._status;
    },
  },
  watch: {
    selectedStatus(newValue) {
      this.$root.$emit("status-filter-changed", newValue);
    },
  },
  created() {
    this.filters = {
      // NOTE: HIDE SEARCHBAR FOR MVP
      // searchText: {
      //   id: "searchText",
      //   name: "Search",
      //   componentType: "searchBar",
      //   order: 0,
      //   placeholder: "Introduce your query",
      // },
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
  gap: $base-space * 2;
  align-items: center;
  padding: $base-space * 2 0;
}
</style>
