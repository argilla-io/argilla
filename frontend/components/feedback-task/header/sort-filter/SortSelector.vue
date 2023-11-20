<template>
  <div class="sort-selector">
    <SortSelectorItem
      v-for="category in selectedSortingItems"
      :key="category.name"
      :category="category"
      :available-categories="nonSelectedSortingItems"
      @clear-category="onClear(category.name)"
      @change-sort-direction="onChangeSortDirection(category.name)"
      @replace-sort-category="
        onReplaceSortCategory(category.name, ...arguments)
      "
    />
    <BaseDropdown
      v-if="nonSelectedSortingItems.length"
      :visible="visibleDropdown"
    >
      <span slot="dropdown-header">
        <BaseButton class="secondary small light" @click="onToggleVisibility">
          + Add another field</BaseButton
        >
      </span>
      <span slot="dropdown-content">
        <SortCategoriesList
          v-click-outside="onToggleVisibility"
          :categories="nonSelectedSortingItems"
          @include-category="includeSortCategory"
        />
      </span>
    </BaseDropdown>
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
    onToggleVisibility() {
      this.visibleDropdown = !this.visibleDropdown;
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
      if (!this.selectedSortingItems.length) {
        this.applySorting();
      }
    },
    onChangeSortDirection(categoryName) {
      this.sortingItems.toggleSort(categoryName);
    },
    onReplaceSortCategory(categoryName, newCategoryName) {
      this.sortingItems.replace(categoryName, newCategoryName);
      this.visibleDropdown = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.sort-selector {
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: $base-space;
}
</style>
