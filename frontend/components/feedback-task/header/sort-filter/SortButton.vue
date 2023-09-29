<template>
  <FilterButton
    button-name="Sort"
    icon-name="sort"
    :show-icon="!!activeSortItemsCounter"
    :is-button-active="isButtonActive"
  >
    <BaseBadge
      class="sort-button__badge"
      v-if="activeSortItemsCounter"
      :text="`Sort (${activeSortItemsCounter})`"
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
  &__badge {
    max-width: 140px;
    background: $black-4;
    border: none;
    font-weight: 500;
    @include line-height(16px);
  }
}
</style>