<template>
  <div>
    <SearchLabelComponent
      v-model="searchText"
      placeholder="Filter by..."
      searchRef="metadataSearch"
      class="category__search"
    />
    <ul class="category__list">
      <li v-for="category in categoriesFilteredBySearchText" :key="category">
        <BaseButton @on-click="selectCategory(category)" class="category__item"
          >{{ category }} <svgicon name="chevron-right" width="8" height="8"
        /></BaseButton>
      </li>
    </ul>
  </div>
</template>
<script>
import "assets/icons/chevron-right";
export default {
  props: {
    categories: {
      type: Array,
      required: true,
    },
  },
  data: () => {
    return {
      searchText: "",
    };
  },
  computed: {
    categoriesFilteredBySearchText() {
      return this.categories.filter((cat) =>
        cat.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
  },
  methods: {
    selectCategory(category) {
      this.$emit("select-category", category);
    },
  },
};
</script>
<style lang="scss" scoped>
.category {
  &__list {
    list-style: none;
    padding-left: 0;
    margin: $base-space 0 0 0;
    overflow: auto;
    max-height: 200px;
  }
  &__item {
    padding: $base-space;
    width: 100%;
    justify-content: space-between;
    border-radius: $border-radius;
    font-weight: 500;
    &:hover {
      background: $black-4;
    }
  }
  &__search {
    width: 100%;
  }
}
</style>
