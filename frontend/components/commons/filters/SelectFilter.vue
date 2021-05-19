<template>
  <div class="filter__row">
    <p class="filter__label" :title="filter.name">{{ filter.name }}:</p>
    <FilterDropdown :class="{ highlighted: visible || appliedFilters.length }" class="dropdown--filter" :visible="visible" @visibility="onVisibility">
      <span slot="dropdown-header">
        <span v-if="appliedFilters.length">
          <p v-if="typeof appliedFilters === 'string'">{{ appliedFilters }}</p>
          <p v-else v-for="appliedFilter in appliedFilters" :key="appliedFilter">{{ appliedFilter }}</p>
        </span>
        <span v-else>
          {{filter.placeholder}}
        </span>
      </span>
      <div slot="dropdown-content">
        <input v-model="searchText" class="filter-options" type="text" autofocus :placeholder="placeholder" />
        <ul>
          <li v-for="(recordsCounter, optionName) in filterOptions(
              filter.options,
              searchText
            )" :key="optionName.index">
            <ReCheckbox class="re-checkbox--dark" :id="optionName" :value="optionName" v-model="selectedOptions">
              {{ optionName }} ({{ recordsCounter }})
            </ReCheckbox>
          </li>
          <li v-if="
              !Object.entries(filterOptions(filter.options, searchText)).length
            ">
            0 results
          </li>
        </ul>
        <div class="filter__buttons">
          <ReButton class="button-tertiary--small button-tertiary--outline" @click="onCancel">
            Cancel
          </ReButton>
          <ReButton class="button-primary--small" @click="onApply">
            Apply
          </ReButton>
        </div>
      </div>
    </FilterDropdown>
  </div>
</template>

<script>
export default {
  props: {
    filter: {
      type: Object,
      default: () => ({}),
    },
    placeholder: {
      type: String,
      required: false,
      default: "Search...",
    },
  },
  watch: {
    appliedFilters() {
      this.selectedOptions = this.appliedFilters;
    }
  },
  mounted() {
    this.selectedOptions = this.appliedFilters;
  },
  data: () => ({
    visible: false,
    searchText: undefined,
    searchTextValue: undefined,
    selectedOptions: [],
  }),
  computed: {
    appliedFilters() {
      return this.filter.selected || [];
    }
  },
  methods: {
    onVisibility(value) {
      this.visible = value;
      this.searchText = undefined;
      this.searchTextValue = undefined;
    },
    onApply() {
      this.$emit("apply", this.filter, this.selectedOptions);
      this.selectedOptions = [];
      this.visible = false;
    },
    onCancel() {
      this.visible = false;
    },
    filterOptions(options, text) {
      if (text === undefined) {
        return options;
      }
      let filtered = Object.fromEntries(
        Object.entries(options).filter(([id, value]) =>
          id.toLowerCase().match(text.toLowerCase())
        )
      );
      return filtered;
    },
  },
};
</script>

<style lang="scss" scoped>
.highlight-text {
  display: inline-block;
  // font-weight: 600;
  background: #ffbf00;
  line-height: 16px;
}

.filter {
  &__row {
    display: flex;
    align-items: center;
    .dropdown {
      margin-right: 0;
      margin-left: auto;
      width: 220px;
      flex-shrink: 0;
    }
  }
  &__label {
    word-break: normal;
    margin: 0 1em 0 0;
    max-width: 166px;
    text-overflow: ellipsis;
    overflow: hidden;
  }
  &__buttons {
    margin-top: 1em;
    text-align: right;
    display: flex;
    & > * {
      margin-right: 0.5em;
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
    .dropdown--open & {
      visibility: hidden;
    }
    & + .dropdown__selectables {
      &:before {
        content: ',  ';
        margin-right: 2px;
      }
      &:after {
        content: '...';
        margin-left: -2px;
      }
    }
  }
}
.filter-options {
  &__back {
    color: $primary-color;
    margin-top: 1em;
    display: flex;
    align-items: center;
    &__chev {
      cursor: pointer;
      margin-right: 1em;
      padding: 0.5em;
      &:after {
        content: '';
        border-color: $primary-color;
        border-style: solid;
        border-width: 1px 1px 0 0;
        display: inline-block;
        height: 8px;
        width: 8px;
        transform: rotate(-135deg);
        transition: all 1.5s ease;
        margin-bottom: 2px;
        margin-left: auto;
        margin-right: 0;
      }
    }
  }
  &__button {
    display: flex;
    cursor: pointer;
    min-width: 135px;
    transition: min-width 0.2s ease;
    &.active {
      min-width: 270px;
      transition: min-width 0.2s ease;
    }
    &.hidden {
      opacity: 0;
    }
  }
  &__chev {
    padding-left: 2em;
    margin-right: 0;
    margin-left: auto;
    background: none;
    border: none;
    outline: none;
    &:after {
      content: '';
      border-color: #4a4a4a;
      border-style: solid;
      border-width: 1px 1px 0 0;
      display: inline-block;
      height: 8px;
      width: 8px;
      transform: rotate(43deg);
      transition: all 1.5s ease;
      margin-bottom: 2px;
      margin-left: auto;
      margin-right: 0;
    }
  }
}
</style>
