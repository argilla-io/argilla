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
          @click-on-clear="clearSortCategory"
        />
      </span>
      <span slot="dropdown-content" class="sort-filter__container">
        <SortCategoriesSelector
          v-if="!categoriesSelected.length"
          class="sort-filter__selector"
          :categories="nonSelectedCategories"
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
      visibleDropdown: false,
    };
  },
  computed: {
    nonSelectedCategories() {
      return this.metadataSort.noSelected;
    },
    categoriesSelected() {
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
    },
    applySort() {
      this.$root.$emit(
        "sort-changed",
        this.categoriesSelected.map((c) => `metadata.${c.name}:${c.sort}`) //Todo order by priority
      );
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
