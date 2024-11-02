<template>
  <div class="sort-filter">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onSortToggleVisibility"
    >
      <span slot="dropdown-header">
        <SortButton
          :is-active="visibleDropdown"
          :active-sort-items="selectedSortingItems"
        />
      </span>
      <span slot="dropdown-content" class="sort-filter__container">
        <SortCategoriesList
          v-if="!selectedSortingItems.length"
          class="sort-filter__selector"
          :categories="nonSelectedSortingItems"
          @include-category="includeSortCategory"
        />
        <SortSelector
          v-else
          :sorting-items="categoriesSort"
          @clear-category="clearSortCategory"
          @apply-sort="applySort"
        />
      </span>
    </BaseDropdown>
  </div>
</template>

<script>
import { useSortRecords } from "./useSortRecords";

export default {
  props: {
    datasetMetadata: {
      type: Array,
      required: true,
    },
    datasetQuestions: {
      type: Array,
      required: true,
    },
    sortFilters: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "sortFilters",
    event: "onSortFilteredChanged",
  },
  data() {
    return {
      visibleDropdown: false,
    };
  },
  computed: {
    nonSelectedSortingItems() {
      return this.categoriesSort.noSelected;
    },
    selectedSortingItems() {
      return this.categoriesSort.selected;
    },
  },
  methods: {
    onSortToggleVisibility(value) {
      this.visibleDropdown = value;
    },
    includeSortCategory(category) {
      this.categoriesSort.select(category);
    },
    clearSortCategory(category) {
      this.categoriesSort.unselect(category);

      this.applySort();
    },
    applySort() {
      this.onSortToggleVisibility(false);

      this.sort();
    },
    sort() {
      if (!this.categoriesSort.hasChanges) return;

      const newSorting = this.categoriesSort.commit();

      this.$emit("onSortFilteredChanged", newSorting);
    },
    updateAppliedCategoriesFromMetadataFilter() {
      if (!this.categoriesSort) return;

      this.categoriesSort.complete(this.sortFilters);
    },
  },
  watch: {
    visibleDropdown() {
      if (!this.visibleDropdown) {
        this.debounce.stop();

        this.sort();
      }
    },
    "categoriesSort.selected": {
      deep: true,
      async handler() {
        this.debounce.stop();

        await this.debounce.wait();

        this.sort();
      },
    },
    sortFilters() {
      this.updateAppliedCategoriesFromMetadataFilter();
    },
  },
  created() {
    this.updateAppliedCategoriesFromMetadataFilter();
  },
  setup(props) {
    return useSortRecords(props);
  },
};
</script>
<style lang="scss" scoped>
$sort-filter-width: 312px;
.sort-filter {
  user-select: none;
  &__container {
    display: block;
    width: $sort-filter-width;
  }
  &__header {
    display: flex;
    gap: $base-space;
    align-items: center;
    justify-content: right;
    padding: $base-space $base-space * 2;
    cursor: pointer;
  }
  &__content {
    padding: $base-space;
  }
  &__categories {
    padding: $base-space;
    background: var(--color-white);
    border-radius: $border-radius;
  }
  :deep(.dropdown__header) {
    background: none;
  }
  :deep(.dropdown__content) {
    right: auto;
    left: 0;
  }
}
</style>
