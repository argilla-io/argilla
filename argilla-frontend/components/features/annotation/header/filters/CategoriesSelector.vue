<template>
  <div>
    <SearchLabelComponent
      v-model="searchText"
      :placeholder="$t('filterBy')"
      :searchRef="name"
      class="category__search"
    />
    <ul class="category__list">
      <li
        v-for="category in categoriesFilteredBySearchText"
        :key="category.name"
        :title="category.tooltip"
      >
        <BaseButton
          @on-click="selectCategory(category)"
          class="category__item"
          :class="category.isAnswered ? 'category__item--selected' : null"
          :disabled="!category.canFilter"
        >
          <span v-if="!!category.title" v-text="category.title" />
          <span v-else>{{ $t(`${prefixTranslation}${category.name}`) }}</span>
          <svgicon name="chevron-right" width="10" height="10"
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
    name: {
      type: String,
      required: true,
    },
    prefixTranslation: {
      type: String,
      default: "",
    },
  },
  data: () => {
    return {
      searchText: "",
    };
  },
  computed: {
    categoriesFilteredBySearchText() {
      return this.categories.filter((cat) => {
        const filterProp = cat.title ?? cat.name;
        return filterProp.toLowerCase().includes(this.searchText.toLowerCase());
      });
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
    width: 100%;
    padding: $base-space;
    justify-content: space-between;
    border-radius: $border-radius;
    font-weight: 400;
    &--selected {
      font-weight: 600;
    }
    span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      @include line-height(16px);
    }
    &:hover {
      background: var(--bg-opacity-4);
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
