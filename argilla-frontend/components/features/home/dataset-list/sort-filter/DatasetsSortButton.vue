<template>
  <FilterButton
    :button-name="$t('sorting.label')"
    icon-name="sort"
    :is-button-active="isButtonActive"
  />
</template>

<script>
import "assets/icons/sort";
export default {
  props: {
    isActive: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    isButtonActive() {
      return this.isActive;
    },
  },
};
</script>

<style lang="scss" scoped>
.filter-button--active {
  background: var(--bg-opacity-4);
  &:hover {
    background: var(--bg-opacity-6);
  }
}
</style>
