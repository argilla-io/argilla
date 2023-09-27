<template>
  <div class="sort-selector">
    <p v-for="category in selectedCategories" :key="category.name">
      <BaseButton
        class="sort-selector__close-button"
        @click="onClear(category.name)"
      >
        <svgicon
          class="sort-selector__close-button__icon"
          name="close"
          width="14"
          height="14" /></BaseButton
      >{{ category.name }}
    </p>
    <BaseButton class="secondary small light sort-selector__add-button"
      >+ Add another field</BaseButton
    >
    <BaseButton
      class="primary small full-width sort-selector__button"
      @on-click="applySorting"
      >Sort</BaseButton
    >
  </div>
</template>
<script>
export default {
  props: {
    sortingItems: {
      type: Array,
      required: true,
    },
  },
  computed: {
    selectedCategories() {
      return this.sortingItems.filter((i) => i.selected);
    },
  },
  methods: {
    applySorting() {
      this.$emit("apply-sort");
    },
    onClear(category) {
      this.sortingItems.find((item) => item.name === category).selected = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.sort-selector {
  padding: $base-space;
  &__add-button {
    margin-bottom: $base-space * 2;
  }
}
</style>