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
  },
  computed: {
    filtersFromVuex() {
      return getFiltersByDatasetId(this.datasetId);
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
    const formattedFilters = this.factoryFiltersForOrm(this.filters);
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
    factoryFiltersForOrm(initialFilters) {
      return Object.keys(initialFilters).map((filter) => {
        return {
          dataset_id: this.datasetId,
          id: this.filters[filter].id,
          name: this.filters[filter].name,
          component_type: this.filters[filter].componentType,
          value: this.filters[filter].value,
          options: this.filters[filter].options,
          placeholder: this.filters[filter].placeholder,
          group_id: this.filters[filter].groupId,
        };
      });
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
