<template>
  <div class="filter__container" v-if="column.filtrable">
    <button
      :data-title="column.tooltip"
      @click="openFilter(column)"
      :class="[visibleFilter || selectedOptions.length ? 'active' : '']"
    >
      <svgicon color="#4C4EA3" name="filter" width="16" />
      {{ column.name }}
    </button>
    <div class="table__filter" v-click-outside="close" v-if="visibleFilter">
      <input
        v-model="searchText"
        class="filter-options"
        type="text"
        autofocus
        placeholder="Search"
      />
      <ul>
        <li
          v-for="option in filterOptions(this.options, searchText)"
          :key="option.index"
        >
          <ReCheckbox
            :id="option"
            v-model="selectedOptions"
            class="re-checkbox--dark"
            :value="option"
          >
            {{ isObject(option) ? `${option.key}: ${option.value}` : option }}
            ({{ tableItemsCounter(option) | formatNumber }})
          </ReCheckbox>
        </li>
        <li
          v-if="!Object.entries(filterOptions(this.options, searchText)).length"
        >
          0 results
        </li>
      </ul>
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
      if (this.filters[this.column.field]) {
        this.selectedOptions = this.filters[this.column.field];
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
      if (!Object.keys(val).length) {
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
      let filtered = options.filter((id) =>
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
  },
};
</script>
<style lang="scss" scoped>
.table__filter {
  background: $bg;
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
  ul {
    list-style: none;
    max-height: 220px;
    overflow-y: auto;
    margin: 0 -1em;
    padding: 0 1em 1em;
    @extend %hide-scrollbar;
  }
  li {
    padding: 0.4em 0;
  }
  .re-checkbox {
    margin: 0;
    width: 100% !important;
    cursor: default;
  }
  ::v-deep .checkbox-label {
    line-height: 13px;
  }
}
.highlight-text {
  display: inline-block;
  // font-weight: 600;
  background: #ffbf00;
  line-height: 16px;
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
      margin-right: 0.5em;
      min-height: 38px;
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
  color: $font-secondary;
  display: flex;
  align-items: center;
  @include font-size(14px);
  font-family: $sff;
  @include media("<=desktop") {
    display: block;
    ::v-deep svg {
      display: block;
      margin-right: 0 !important;
    }
  }
  &:hover,
  &.active {
    background: $bg;
    min-height: 40px;
    padding: 0 1em;
    margin: 0 -1em;
    border-radius: $border-radius;
    color: $primary-color;
    ::v-deep svg {
      & > * {
        fill: $primary-color !important;
      }
    }
  }
  .svg-icon {
    margin-right: 8px;
  }
}
</style>
