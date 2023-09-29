<template>
  <FilterButton
    button-name="Sort"
    icon-name="sort"
    :show-icon="!!activeSortItemsCounter"
    :is-button-active="isButtonActive"
  >
    <span
      class="sort-button__text"
      v-if="activeSortItemsCounter"
      v-text="`Sort (${activeSortItemsCounter})`"
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
.sort-button {
  &__text {
    @include font-size(13px);
    font-weight: 500;
  }
}
</style>