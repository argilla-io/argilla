<template>
  <FilterButton
    :button-name="$t('sorting.label')"
    icon-name="sort"
    :is-button-active="isButtonActive"
  >
    <span
      class="sort-button__text"
      v-if="activeSortItemsCounter"
      v-text="`(${activeSortItemsCounter})`"
    />
  </FilterButton>
</template>

<script>
import "assets/icons/sort";
export default {
  props: {
    activeSortItems: {
      type: Array,
      default: () => [],
    },
    isActive: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    isButtonActive() {
      return this.isActive || !!this.activeSortItemsCounter;
    },
    activeSortItemsCounter() {
      return this.activeSortItems.length;
    },
  },
};
</script>

<style lang="scss" scoped>
.filter-button--active {
  background: none;
  &:hover {
    background: var(--bg-opacity-4);
  }
}
</style>
