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
    <BaseDropdown :visible="visibleDropdown" @visibility="onToggleVisibility">
      <span slot="dropdown-header">
        {{ category.name }}
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
        width="24"
        height="24"
        :name="category.sort === 'asc' ? 'arrow-up' : 'arrow-down'"
      />
    </BaseButton>
  </div>
</template>

<script>
import "assets/icons/close";
import "assets/icons/arrow-up";
import "assets/icons/arrow-down";
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
  justify-content: space-between;
}
</style>