<template>
  <div class="sort-selector">
    <SortSelectorItem
      v-for="category in selectedSortingItems"
      :key="category.id"
      :category="category"
      :available-categories="nonSelectedSortingItems"
      @clear-category="onClear(category)"
      @change-sort-direction="onChangeSortDirection(category)"
      @replace-sort-category="onReplaceSortCategory(category, ...arguments)"
    />
    <BaseDropdown
      v-if="nonSelectedSortingItems.length"
      :visible="visibleDropdown"
    >
      <span slot="dropdown-header">
        <BaseButton class="secondary small light" @click="onToggleVisibility">
          {{ $t("sorting.addOtherField") }}</BaseButton
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
    includeSortCategory(category) {
      this.sortingItems.select(category);

      this.visibleDropdown = false;
    },
    applySorting() {
      this.$emit("apply-sort");
    },
    onClear(category) {
      this.sortingItems.unselect(category);

      if (!this.selectedSortingItems.length) {
        this.applySorting();
      }
    },
    onChangeSortDirection(category) {
      this.sortingItems.toggleSort(category);
    },
    onReplaceSortCategory(category, newCategory) {
      this.sortingItems.replace(category, newCategory);
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
