<template>
  <div class="filter--sort">
    <FilterDropdown
      :class="{ highlighted: visible }"
      class="dropdown--filter dropdown--sortable"
      :visible="visible"
      @visibility="onVisibility"
    >
      <span slot="dropdown-header">
        <span v-if="optionSelected" class="dropdown__selectables"
          >{{ selectedSortedBy.text }}
          {{ sortedRange(selectedSortedBy, defaultSortedByDir) }}</span
        >
        <span v-else>Sort by</span>
      </span>
      <div slot="dropdown-content">
        <ul class="dropdown__list">
          <span v-for="option in sortOptions" :key="option.text">
            <div
              v-for="sortOption in sortOrder"
              :key="sortOption.index"
              class="dropdown__list__item"
              @click="sort(option.filter, sortOption)"
            >
              <li v-if="notSelectedOption(option, sortOption)">
                {{ option.text }} {{ sortedRange(option, sortOption) }}
              </li>
            </div>
          </span>
          <li
            v-if="optionSelected"
            class="dropdown__list__item"
            @click="sortDefault()"
          >
            Default
          </li>
        </ul>
      </div>
    </FilterDropdown>
  </div>
</template>

<script>
export default {
  props: {
    sortOptions: {
      type: Array,
      required: true,
      validator(options) {
        return (
          options.length > 0 &&
          options.find(
            ({ filter, text, range }) =>
              filter === undefined || text === undefined || range === undefined
          ) === undefined
        );
      },
    },
  },
  data: () => ({
    visible: false,
    defaultSortedBy: undefined,
    defaultSortedByDir: "asc",
    optionSelected: false,
    sortOrder: ["asc", "desc"],
  }),
  computed: {
    selectedSortedBy() {
      const key = Object.keys(this.sortOptions).find(
        (k) => this.sortOptions[k].filter === this.defaultSortedBy
      );
      return this.sortOptions[key] || this.sortOptions[0];
    },
  },
  methods: {
    onVisibility(value) {
      this.visible = value;
    },
    sortDefault() {
      this.sort("default");
      this.optionSelected = false;
    },
    sort(currentSort, currentSortDir) {
      this.visible = false;
      this.optionSelected = true;
      this.defaultSortedBy = currentSort;
      this.defaultSortedByDir = currentSortDir;
      if (currentSort === "default") {
        this.$emit("defaultSort");
      } else {
        this.$emit("sort", currentSort, currentSortDir);
      }
    },
    notSelectedOption(option, sortOption) {
      if (
        sortOption === this.defaultSortedByDir &&
        option.filter === this.defaultSortedBy
      ) {
        return false;
      }
      return true;
    },
    sortedRange(by, byDir) {
      return `${by.range[byDir === this.sortOrder[0] ? 0 : 1]} - ${by.range[byDir === this.sortOrder[0] ? 1 : 0]
        }`;
    },
  },
};
</script>

<style lang="scss" scoped>
.filter {
  &--sort {
    margin-right: 0;
    margin-left: 3em;
    display: flex;
    padding: 0;
    .filter:last-child {
      margin-right: 0;
      margin-left: auto;
      padding-right: 0;
    }
  }
}
.dropdown {
  &__placeholder {
    display: none;
    .dropdown--open & {
      display: block;
    }
  }
  &__selectables {
    vertical-align: middle;
    display: inline-block;
    .dropdown--open & {
      display: none;
    }
    & + .dropdown__selectables {
      &:before {
        content: ",  ";
        margin-right: 2px;
      }
      &:after {
        content: "...";
        margin-left: -2px;
      }
    }
  }
  &__list {
    padding-right: 0;
    &__item {
      cursor: pointer;
      &:hover {
        color: $secondary-color;
      }
    }
  }
}
</style>
