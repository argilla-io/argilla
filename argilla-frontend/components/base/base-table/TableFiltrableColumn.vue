<template>
  <div class="filter__container" v-if="column.filtrable">
    <button
      :data-title="column.tooltip"
      @click="openFilter(column)"
      :class="[visibleFilter || selectedOptions.length ? 'active' : '']"
    >
      <svgicon name="filter" width="16" aria-hidden="true" />
      {{ column.name }}
    </button>
    <div class="table__filter" v-click-outside="close" v-if="visibleFilter">
      <select-options-search v-model="searchText" />
      <select-options
        ref="options"
        type="multiple"
        v-model="selectedOptions"
        :options="filterOptions(this.options, searchText)"
        :option-name="optionName"
        :option-counter="optionCounter"
        :aria-label="optionName"
      />
    </div>
  </div>
</template>

<script>
import "assets/icons/filter";
export default {
  props: {
    column: {
      type: Object,
      required: true,
    },
    filters: {
      type: Object,
      required: true,
    },
    data: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      searchText: undefined,
      visibleFilter: false,
      selectedOptions: [],
    };
  },
  mounted() {
    this.$nextTick(() => {
      const filter = this.filters[this.column.field];
      if (filter) {
        if (filter.every(this.isObject)) {
          this.selectedOptions = this.options.filter((option) =>
            filter.some((f) => f.key === option.key && f.value === option.value)
          );
        } else {
          this.selectedOptions = filter;
        }
      }
    });
  },
  computed: {
    options() {
      const rawOptions = this.data.map((item) => item[this.column.field]);
      if (rawOptions.every((option) => this.isObject(option))) {
        const removedEmptyOptions = rawOptions
          .filter((opt) => Object.values(opt).length)
          .flatMap((opt) => opt);
        const optionsArray = Object.values(removedEmptyOptions).flatMap(
          (options) =>
            Object.keys(options).map((key) => {
              return { key: key, value: options[key] };
            })
        );
        const keys = ["key", "value"];
        return optionsArray.filter(
          (
            (s) => (o) =>
              ((k) => !s.has(k) && s.add(k))(keys.map((k) => o[k]).join("|"))
          )(new Set())
        );
      } else {
        return [...new Set(rawOptions)];
      }
    },
  },
  watch: {
    selectedOptions() {
      this.$emit("applyFilters", this.column, this.selectedOptions);
    },
    filters(val) {
      if (!Object.keys(val).length && this.selectedOptions.length) {
        this.selectedOptions = [];
      }
    },
  },
  methods: {
    isObject(obj) {
      return Object.prototype.toString.call(obj) === "[object Object]";
    },
    openFilter() {
      this.visibleFilter = true;
    },
    close() {
      this.visibleFilter = false;
    },
    filterOptions(options, text) {
      if (text === undefined) {
        return options;
      }
      const filtered = options.filter((id) =>
        JSON.stringify(id).toLowerCase().match(text.toLowerCase())
      );
      return filtered;
    },
    tableItemsCounter(option) {
      const keys = Object.keys(this.filters).filter(
        (k) => k !== this.column.field
      );
      const filteredData = this.data.filter((tableItem) => {
        return keys.every((key) => {
          if (this.filters[key].every((f) => this.isObject(f))) {
            return this.filters[key].find(
              (f) => f.value === tableItem[key][f.key]
            );
          } else {
            return this.filters[key].includes(tableItem[key]);
          }
        });
      });
      if (
        filteredData.every((data) => this.isObject(data[this.column.field]))
      ) {
        return filteredData.filter(
          (tableItem) =>
            tableItem[this.column.field][option.key] === option.value
        ).length;
      } else {
        return filteredData.filter(
          (tableItem) => tableItem[this.column.field] === option
        ).length;
      }
    },
    optionName(option) {
      return this.isObject(option) ? `${option.key}: ${option.value}` : option;
    },
    optionCounter(option) {
      return this.tableItemsCounter(option);
    },
  },
};
</script>
<style lang="scss" scoped>
.table__filter {
  background: var(--bg-accent-grey-3);
  position: absolute;
  top: 50px;
  left: -1em;
  margin-top: 0;
  padding: 10px 20px;
  z-index: 3;
  transform: translate(0);
  right: auto;
  min-width: 270px;
  border-radius: $border-radius;
  box-shadow: $shadow;
}

.filter {
  &__container {
    position: relative;
  }
  &__buttons {
    margin-top: 1em;
    text-align: right;
    display: flex;
    & > * {
      display: block !important;
      width: 100%;
      margin-right: $base-space;
      &:last-child {
        margin-right: 0;
      }
    }
  }
}
.filter-options {
  border: none;
  outline: none;
  height: 40px;
  background: transparent;
}
button {
  cursor: pointer;
  border: 0;
  outline: none;
  background: transparent;
  padding-left: 0;
  padding-right: 0;
  display: flex;
  align-items: center;
  @include font-size(14px);
  @include media("<=desktop") {
    display: block;
    :deep(svg) {
      display: block;
      margin-right: 0 !important;
    }
  }
  &:hover,
  &.active {
    background: var(--bg-opacity-4);
    min-height: 40px;
    padding: 0 1em;
    margin: 0 -1em;
    border-radius: $border-radius;
  }
  .svg-icon {
    margin-right: $base-space;
  }
}
</style>
