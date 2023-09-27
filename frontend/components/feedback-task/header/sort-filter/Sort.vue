<template>
  <div class="sort-filter">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onSortToggleVisibility"
    >
      <span slot="dropdown-header">
        <FilterButton
          button-name="Sort"
          icon-name="sort"
          :badges="appliedSortCategories"
          @click-on-clear="clearSortCategory"
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
    metadata: {
      type: Array,
      required: true,
    },
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
    selectedCategories() {
      return this.selectedSortingItems.map((i) => i.name);
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
      this.$root.$emit(
        "sort-changed",
        this.selectedSortingItems.map((c) => `metadata.${c.name}:${c.sort}`)
      );

      const newSortBy = this.selectedCategories.filter(
        (category) => !this.appliedSortCategories.includes(category)
      );
      if (newSortBy.length) {
        newSortBy.forEach((f) => {
          this.appliedSortCategories.push(f);
        });
      } else {
        this.appliedSortCategories = this.selectedCategories;
      }
    },
  },
  setup(props) {
    return useSortRecords(props);
  },
};
</script>
<style lang="scss" scoped>
$sort-filter-width: 300px;
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
