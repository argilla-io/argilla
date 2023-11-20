<template>
  <div class="sort-categories">
    <SearchLabelComponent
      v-model="searchText"
      :placeholder="$t('filterBy')"
      class="sort-categories__search"
      searchRef="sortFilter"
    />
    <ul class="sort-categories__list">
      <template v-for="group in filteredGroups">
        <span class="sort-categories__group" :key="group" v-text="group" />
        <li
          v-for="category in getCategoriesByGroup(group)"
          :key="category.name"
        >
          <BaseButton
            :disabled="!category.canSort"
            @on-click="includeCategory(category)"
            class="sort-categories__item"
            ><span>{{ category.title }}</span></BaseButton
          >
        </li>
      </template>
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
    sortGroups: {
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
        cat.title.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
    filteredGroups() {
      const groups = this.categoriesFilteredBySearchText.map(
        (cat) => cat.group
      );
      return this.sortGroups.filter((group) => groups.includes(group));
    },
  },
  methods: {
    includeCategory(category) {
      this.$emit("include-category", category.name);
    },
    getCategoriesByGroup(group) {
      return this.categoriesFilteredBySearchText.filter(
        (cat) => cat.group === group
      );
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
  &__group {
    display: inline-block;
    padding: $base-space * 2 $base-space 0 $base-space;
    color: $black-37;
    @include font-size(10px);
    text-transform: uppercase;
    font-weight: 400;
    &:first-of-type {
      padding-top: 0;
    }
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
      @include line-height(16px);
      font-weight: 400;
    }
    &:hover {
      background: $black-4;
    }
    &:focus {
      outline: none;
    }
  }
  &__search {
    min-width: 100%;
  }
}
</style>
