<template>
  <div class="filters">
    <form @submit.prevent="onSearch">
      <span
        class="filters__component"
        v-for="filter in clonedFiltersFromOrm"
        :key="filter.id"
      >
        <SearchBarBase
          v-if="filter.component_type === 'searchBar'"
          v-model.lazy.trim="filter.value"
          :placeholder="filter.placeholder"
        />
      </span>
    </form>
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
  data() {
    return {
      clonedFiltersFromOrm: null,
    };
  },
  created() {
    this.filters = {
      searchText: {
        id: "searchText",
        name: "Search",
        componentType: "searchBar",
        order: 0,
        placeholder: "Introduce your query",
        value: "babidibou",
      },
    };
    const filterValues = Object.values(this.filters);
    const formattedFilters = this.factoryFiltersForOrm(filterValues);
    upsertDatasetFilters(formattedFilters);
  },
  beforeMount() {
    this.filtersFromOrm = getFiltersByDatasetId(
      this.datasetId,
      this.orderBy?.orderFilterBy,
      this.orderBy?.ascendent
    );

    this.clonedFiltersFromOrm = structuredClone(this.filtersFromOrm);
  },
  methods: {
    onSearch() {
      console.log(this.clonedFiltersFromOrm);
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
