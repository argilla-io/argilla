<template>
  <div class="sort-filter">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onSortToggleVisibility"
    >
      <span slot="dropdown-header">
        <SortButton
          :is-active="visibleDropdown"
          :active-sort-items="appliedSortCategories"
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
          :sorting-items="metadataSort"
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
      appliedSortCategories: [],
      visibleDropdown: false,
    };
  },
  computed: {
    nonSelectedSortingItems() {
      return this.metadataSort.noSelected;
    },
    selectedSortingItems() {
      return this.metadataSort.selected;
    },
  },
  methods: {
    onSortToggleVisibility(value) {
      this.visibleDropdown = value;
    },
    includeSortCategory(category) {
      this.metadataSort.select(category);
    },
    clearSortCategory(category) {
      this.metadataSort.unselect(category);

      this.applySort();
    },
    applySort() {
      this.onSortToggleVisibility(false);

      this.sort();
    },
    sort() {
      if (!this.metadataSort.hasChanges) return;

      const newSorting = this.metadataSort.commit();

      this.$emit("onSortFilteredChanged", newSorting);

      this.appliedSortCategories = this.metadataSort.selectedCategoriesName;
    },
    updateAppliedCategoriesFromMetadataFilter() {
      if (!this.metadataSort) return;

      this.metadataSort.initializeWith(this.sortFilters);

      this.appliedSortCategories = this.metadataSort.selectedCategoriesName;
    },
  },
  watch: {
    visibleDropdown() {
      if (!this.visibleDropdown) {
        this.debounce.stop();

        this.sort();
      }
    },
    "metadataSort.selected": {
      deep: true,
      async handler() {
        this.debounce.stop();

        await this.debounce.wait();

        this.sort();
      },
    },
    sortFilters() {
      if (!this.metadataSort.hasDifferencesWith(this.sortFilters)) return;

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
    background: palette(white);
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
