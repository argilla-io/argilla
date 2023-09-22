<template>
  <div>
    <SearchLabelComponent
      v-model="searchText"
      placeholder="Filter by..."
      searchRef="metadataSearch"
    />
    <ul class="category__list">
      <li v-for="category in categoriesFilteredBySearchText" :key="category">
        <BaseButton @on-click="selectCategory(category)">{{
          category
        }}</BaseButton>
      </li>
    </ul>
  </div>
</template>
<script>
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
  }
}
</style>
