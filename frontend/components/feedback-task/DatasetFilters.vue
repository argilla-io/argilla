<template>
  <div class="filters">
    <span v-for="id in Object.keys(this.filters)" :key="id">
      <SearchBar
        v-if="hasComponentsType(id)"
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
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    filters: {
      type: Object,
    },
  },
  computed: {
    filtersFromVuex() {
      return getFiltersByDatasetId(this.datasetId);
    },
  },
  created() {
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
    hasComponentsType(id) {
      return this.filters[id].componentType;
    },
    factoryFiltersForOrm(initialFilters) {
      return Object.keys(initialFilters).map((filter, index) => {
        return {
          dataset_id: this.datasetId,
          id: this.filters[filter].id,
          name: this.filters[filter].name,
          component_type: this.filters[filter].componentType,
          value: this.filters[filter].value,
          options: this.filters[filter].options,
          placeholder: this.filters[filter].placeholder,
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
}
</style>