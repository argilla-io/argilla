<template>
  <div class="sort-selector">
    <SortSelectorItem
      v-for="category in selectedSortingItems"
      :key="category.name"
      :category="category"
      :available-categories="nonSelectedSortingItems"
      @clear-category="onClear(category.name)"
      @change-sort-direction="onChangeSortDirection(category.name)"
      @replace-sort-category="onReplaceSortCategory(category.name)"
    />
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onToggleVisibility"
      v-if="nonSelectedSortingItems.length"
    >
      <span slot="dropdown-header">
        <BaseButton class="secondary small light sort-selector__add-button"
          >+ Add another field</BaseButton
        >
      </span>
      <span slot="dropdown-content">
        <SortCategoriesList
          :categories="nonSelectedSortingItems"
          @include-category="includeSortCategory"
        ></SortCategoriesList>
      </span>
    </BaseDropdown>
    <BaseButton
      class="primary small full-width sort-selector__button"
      @on-click="applySorting"
      >Sort</BaseButton
    >
  </div>
</template>
<script>
export default {
  props: {
    sortingItems: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      visibleDropdown: false,
    };
  },
  computed: {
    nonSelectedSortingItems() {
      return this.sortingItems.noSelected;
    },
    selectedSortingItems() {
      return this.sortingItems.selected;
    },
  },
  methods: {
    onToggleVisibility(value) {
      this.visibleDropdown = value;
    },
    includeSortCategory(categoryName) {
      this.sortingItems.select(categoryName);

      this.visibleDropdown = false;
    },
    applySorting() {
      this.$emit("apply-sort");
    },
    onClear(categoryName) {
      this.sortingItems.unselect(categoryName);
    },
    onChangeSortDirection(categoryName) {
      this.sortingItems.toggleSort(categoryName);
    },
    onReplaceSortCategory(categoryName) {
      this.includeSortCategory(categoryName);

      this.$emit("replace-category-name");
    },
  },
};
</script>

<style lang="scss" scoped>
.sort-selector {
  padding: $base-space;
  &__add-button {
    margin-bottom: $base-space * 2;
  }
}
</style>
