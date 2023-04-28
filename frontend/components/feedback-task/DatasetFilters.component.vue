<template>
  <div class="filters">
    <span
      class="filters__component"
      v-for="id in Object.keys(this.filters)"
      :key="id"
    >
      <SearchBarBase
        v-if="getFilterById(id).component_type === 'searchBar'"
        :current-search-text="getFilterById(id).value"
        @on-search-text="onSearch(id, $event)"
        :placeholder="getFilterById(id).placeholder"
      />
    </span>
  </div>
</template>

<script>
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
  computed: {
    filtersFromVuex() {
      return getFiltersByDatasetId(
        this.datasetId,
        this.orderBy?.orderFilterBy,
        this.orderBy?.ascendent
      );
    },
  },
  created() {
    this.filters = {
      searchText: {
        id: "searchText",
        name: "Search",
        componentType: "searchBar",
        placeholder: "Introduce your query",
      },
    };
    const filterEntries = Object.entries(this.filters);
    const formattedFilters = this.factoryFiltersForOrm(filterEntries);
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
    factoryFiltersForOrm(filtersEntries) {
      return filtersEntries.map(
        ([
          fileName,
          { id, name, componentType, value, options, placeholder, groupId },
        ]) => {
          return {
            dataset_id: this.datasetId,
            id,
            name,
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
};
</script>

<style lang="scss" scoped>
.filters {
  display: flex;
  gap: $base-space * 2;
  align-items: center;
  padding: $base-space * 2 0;
  &__component {
    flex: 1;
  }
}
</style>
