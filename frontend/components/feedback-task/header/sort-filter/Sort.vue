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
      appliedSortCategories: [],
      visibleDropdown: false,
      sortingItems: [
        { name: "lorem", sort: "asc", selected: false },
        { name: "lorem1", sort: "asc", selected: false },
        { name: "lorem2", sort: "desc", selected: true },
      ],
    };
  },
  computed: {
    nonSelectedSortingItems() {
      return this.sortingItems.filter((f) => !f.selected).map((f) => f.name);
    },
    selectedSortingItems() {
      return this.sortingItems.filter((i) => i.selected);
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
      this.sortingItems.find((item) => item.name === category).selected = true;
    },
    clearSortCategory(category) {
      this.sortingItems.find((item) => item.name === category).selected = false;
      this.applySort();
    },
    applySort() {
      this.$root.$emit(
        "sort-changed",
        this.selectedSortingItems.map((c) => `metadata.${c.name}:${c.sort}`) //Todo order by priority
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
