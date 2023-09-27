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
          :badges="appliedSortFilters"
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
          :sorting-items="sortingItems"
          @clear-category="clearSortCategory"
          @apply-sort="applySort"
        />
      </span>
    </BaseDropdown>
  </div>
</template>

<script>
export default {
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      visibleDropdown: false,
      sortingItems: [
        { name: "lorem", sort: "asc", selected: false },
        { name: "lorem1", sort: "asc", selected: false },
        { name: "lorem2", sort: "asc", selected: true },
      ],
    };
  },
  computed: {
    nonSelectedCategories() {
      return this.sortingItems.filter((f) => !f.selected).map((f) => f.name);
    },
    categoriesSelected() {
      return this.sortingItems.filter((i) => i.selected);
    },
  },
  methods: {
    onSortToggleVisibility(value) {
      this.visibleDropdown = value;
    },
    includeSortCategory(category) {
      this.sortingItems.find((item) => item.name === category).selected = true;
    },
    clearSortCategory(category) {
      this.sortingItems.find((item) => item.name === category).selected = false;
    },
    applySort() {
      this.$root.$emit(
        "sort-changed",
        this.categoriesSelected.map((c) => `metadata.${c.name}:${c.sort}`) //Todo order by priority
      );
    },
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
