<template>
  <div class="sort-selector-item">
    <BaseButton
      class="sort-selector-item__close-button"
      @click="$emit('clear-category')"
    >
      <svgicon
        class="sort-selector-item__close-button__icon"
        name="close"
        width="14"
        height="14"
    /></BaseButton>
    <BaseDropdown
      :visible="visibleDropdown"
      @visibility="onToggleVisibility"
      class="sort-selector-item__dropdown"
    >
      <span slot="dropdown-header" class="sort-selector-item__dropdown__header">
        <span
          class="sort-selector-item__dropdown__header__text"
          title="category.name"
          v-text="category.name"
        />
        <svgicon width="12" height="12" name="chevron-down" />
      </span>
      <span slot="dropdown-content">
        <SortCategoriesList
          :categories="availableCategories"
          @include-category="changeCategoryName"
        ></SortCategoriesList>
      </span>
    </BaseDropdown>
    <BaseButton
      title="sort direction"
      class="sort-selector-item__direction secondary light"
      @click="$emit('change-sort-direction')"
    >
      <svgicon
        width="16"
        height="16"
        :name="category.sort === 'asc' ? 'arrow-up' : 'arrow-down'"
      />
    </BaseButton>
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
    changeCategoryName() {
      console.log("change selected category name");
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
      width: 100%;
      padding: $base-space;
      border: 1px solid $black-10;
      border-radius: $border-radius;
      cursor: pointer;
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
