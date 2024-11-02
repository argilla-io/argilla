<template>
  <div class="sort-selector-item">
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onToggleVisibility"
      class="sort-selector-item__dropdown"
    >
      <span slot="dropdown-header" class="sort-selector-item__dropdown__header">
        <div class="sort-selector-item__dropdown__header__item">
          <span
            class="sort-selector-item__dropdown__header__group"
            v-text="$t(`sorting.${category.group}`)"
          />
          <span
            class="sort-selector-item__dropdown__header__text"
            title="category.title"
            v-text="category.title"
          />
        </div>
        <svgicon width="12" height="12" name="chevron-down" />
      </span>
      <span slot="dropdown-content">
        <SortCategoriesList
          v-if="availableCategories.length"
          :categories="availableCategories"
          @include-category="replaceCategory"
        ></SortCategoriesList>
      </span>
    </BaseDropdown>
    <BaseButton
      title="sort direction"
      class="sort-selector-item__direction secondary clear"
      @click="$emit('change-sort-direction')"
    >
      <svgicon
        width="16"
        height="16"
        :name="category.sort === 'asc' ? 'arrow-up' : 'arrow-down'"
        :aria-label="
          'Change sort direction to ' +
          (category.sort === 'asc' ? 'up' : 'down')
        "
      />
    </BaseButton>
    <BaseButton
      class="sort-selector-item__close-button secondary clear"
      @click="$emit('clear-category')"
    >
      <svgicon
        class="sort-selector-item__close-button__icon"
        name="close"
        width="14"
        height="14"
    /></BaseButton>
  </div>
</template>

<script>
import "assets/icons/close";
import "assets/icons/arrow-up";
import "assets/icons/arrow-down";
import "assets/icons/chevron-down";
export default {
  props: {
    category: {
      type: Object,
    },
    availableCategories: {
      type: Array,
    },
  },
  data: () => {
    return {
      visibleDropdown: false,
    };
  },
  methods: {
    onToggleVisibility(value) {
      this.visibleDropdown = value;
    },
    replaceCategory(category) {
      this.$emit("replace-sort-category", category);
      this.visibleDropdown = false;
    },
  },
};
</script>
<style lang="scss" scoped>
.sort-selector-item {
  display: flex;
  align-items: center;
  gap: $base-space;
  &__dropdown {
    width: 100%;
    min-width: 0;
    &__header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-direction: row;
      width: 100%;
      padding: calc($base-space / 2) $base-space;
      border: 1px solid var(--bg-opacity-10);
      border-radius: $border-radius;
      cursor: pointer;
      &__item {
        display: flex;
        flex-direction: column;
        width: 90%;
      }
      &__group {
        margin-top: calc($base-space / 2 * -1);
        color: var(--fg-tertiary);
        @include font-size(10px);
        text-transform: capitalize;
      }
      &__text {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
      .svg-icon {
        flex-shrink: 0;
      }
    }
  }
  &__close-button {
    flex-shrink: 0;
    padding: $base-space;
  }
  &__direction {
    flex-shrink: 0;
    padding: $base-space;
  }
}
</style>
