<template>
  <div class="sort-filter">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onSortToggleVisibility"
    >
      <span slot="dropdown-header">
        <DatasetsSortButton :is-active="visibleDropdown" />
      </span>
      <span slot="dropdown-content" class="sort-filter__container">
        <DatasetsSortSelectorItem
          :selected-option="sortedByField"
          :selected-direction="sortedOrder"
          :options="sortOptions"
          @change-sort-direction="$emit('on-change-direction', $event)"
          @change-sort-field="$emit('on-change-field', $event)"
        />
      </span>
    </BaseDropdown>
  </div>
</template>

<script>
export default {
  props: {
    sortedByField: {
      type: String,
      required: true,
    },
    sortedOrder: {
      type: String,
      required: true,
    },
    sortOptions: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      visibleDropdown: false,
    };
  },
  methods: {
    onSortToggleVisibility(value) {
      this.visibleDropdown = value;
    },
  },
};
</script>
<style lang="scss" scoped>
$sort-filter-width: 312px;
.sort-filter {
  user-select: none;
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
    background: var(--color-white);
    border-radius: $border-radius;
  }
  :deep(.dropdown__header) {
    background: none;
  }
  :deep(.dropdown__content) {
    right: 0;
    left: auto;
  }
}
</style>
