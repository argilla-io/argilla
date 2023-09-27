<template>
  <div class="sort-categories">
    <SearchLabelComponent
      v-model="searchText"
      :placeholder="$t('filterBy')"
      class="sort-categories__search"
      searchRef="sortFilter"
    />
    <ul class="sort-categories__list">
      <li
        v-for="category in categoriesFilteredBySearchText"
        :key="category.name"
      >
        <BaseButton
          @on-click="includeCategory(category)"
          class="sort-categories__item"
          ><span>{{ category.name }}</span></BaseButton
        >
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
        cat.name.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
  },
  methods: {
    includeCategory(category) {
      this.$emit("include-category", category.name);
    },
  },
};
</script>
<style lang="scss" scoped>
.sort-categories {
  padding: $base-space;
  &__list {
    list-style: none;
    padding-left: 0;
    margin: $base-space 0 0 0;
    overflow: auto;
    max-height: 200px;
  }
  &__item {
    width: 100%;
    padding: $base-space;
    justify-content: space-between;
    border-radius: $border-radius;
    font-weight: 500;
    span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    &:hover {
      background: $black-4;
    }
  }
  &__search {
    min-width: 100%;
  }
}
</style>
