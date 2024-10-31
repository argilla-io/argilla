<!--
  - coding=utf-8
  - Copyright 2021-present, the Recognai S.L. team.
  -
  - Licensed under the Apache License, Version 2.0 (the "License");
  - you may not use this file except in compliance with the License.
  - You may obtain a copy of the License at
  -
  -     http://www.apache.org/licenses/LICENSE-2.0
  -
  - Unless required by applicable law or agreed to in writing, software
  - distributed under the License is distributed on an "AS IS" BASIS,
  - WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  - See the License for the specific language governing permissions and
  - limitations under the License.
  -->
<template>
  <transition appear name="fade">
    <div class="table-info" role="table">
      <div class="table-info__header">
        <slot name="columns">
          <div
            class="table-info__item"
            role="columnheader"
            aria-label="Table Header"
          >
            <div
              v-for="(column, key) in columns"
              :key="key"
              :class="[`table-info__item__col`, column.class]"
              :aria-label="column.name"
              role="cell"
            >
              <lazy-table-filtrable-column
                :column="column"
                :data="data"
                :filters="filters"
                v-if="column.filtrable"
                @applyFilters="onApplyFilters"
                :aria-label="'Filter column ' + column.name"
              />
              <button
                v-else-if="column.sortable"
                :data-title="column.tooltip"
                :class="[sortOrder, { active: sortedBy === column.field }]"
                @click="sort(column)"
                :aria-label="'Sort by ' + column.name"
                :aria-sort="sortOrder === 'asc' ? 'descending' : 'ascending'"
              >
                <svgicon
                  width="18"
                  height="18"
                  name="sort"
                  aria-hidden="true"
                />
                <span>{{ column.name }}</span>
              </button>
              <button v-else :data-title="column.tooltip">
                <span>{{ column.name }}</span>
              </button>
            </div>
          </div>
        </slot>
      </div>
      <results-empty v-if="tableIsEmpty" :title="emptySearchInfo.title" />
      <template v-else>
        <div class="table-info__body" ref="table" aria-label="Table Body">
          <ul role="rowgroup">
            <li
              v-for="item in filteredResults"
              :key="item.id"
              :id="item.id"
              role="row"
              :aria-label="'Row for ' + item.id"
            >
              <nuxt-link :to="rowLink(item)" class="table-info__item">
                <span
                  v-for="(column, idx) in columns"
                  :key="idx"
                  :class="[`table-info__item__col`, column.class]"
                  role="cell"
                >
                  <span :class="column.class">
                    <span
                      v-if="column.actions"
                      role="group"
                      aria-label="Row actions"
                    >
                      <div class="table-info__actions">
                        <p
                          class="table-info__main"
                          v-if="column.type === 'main'"
                        >
                          {{ itemValue(item, column) }}
                        </p>
                        <span v-else>{{ itemValue(item, column) }}</span>
                        <div class="table-info__actions__buttons">
                          <base-action-tooltip
                            v-for="(action, idx) in column.actions"
                            :key="idx"
                            :tooltip="action.tooltip"
                            role="button"
                            :aria-label="action.title"
                          >
                            <base-button
                              :title="action.title"
                              class="table-info__actions__button"
                              @click.prevent="
                                onActionClicked(action.name, item)
                              "
                              aria-hidden="true"
                            >
                              <svgicon
                                v-if="action.icon !== undefined"
                                :name="action.icon"
                                width="16"
                                height="16"
                                aria-hidden="true"
                              />
                            </base-button>
                          </base-action-tooltip>
                        </div>
                      </div>
                    </span>
                    <base-date
                      v-else-if="column.type === 'date'"
                      format="date-relative-now"
                      :date="itemValue(item, column)"
                    />
                    <nuxt-link v-else-if="column.link" :to="column.link(item)">
                      {{ itemValue(item, column) }}
                    </nuxt-link>
                    <span v-else>{{ itemValue(item, column) }}</span>
                    <span v-if="column.component">
                      <component
                        :aria-label="column.component.name"
                        v-if="hydrate[item.id]"
                        :is="column.component.name"
                        v-bind="{ ...column.component.props(item) }"
                      />
                    </span>
                  </span>
                </span>
              </nuxt-link>
            </li>
          </ul>
        </div>
      </template>
    </div>
  </transition>
</template>

<script>
import "assets/icons/trash-empty";
import "assets/icons/refresh";
import "assets/icons/copy";
import "assets/icons/settings";
import "assets/icons/link";
import "assets/icons/sort";

export default {
  props: {
    data: {
      type: Array,
      default: () => [],
    },
    columns: {
      type: Array,
      required: true,
    },
    sortedOrder: {
      type: String,
      default: "desc",
    },
    searchOn: {
      type: String,
      required: true,
    },
    sortedByField: {
      type: String,
      default: undefined,
    },
    emptySearchInfo: {
      title: undefined,
    },
    querySearch: {
      type: String,
      default: undefined,
    },
    activeFilters: {
      type: Array,
      default: () => {
        return [];
      },
    },
    rowLink: {
      type: Function,
      default: () => {
        return () => {};
      },
    },
  },
  data() {
    return {
      sortOrder: this.sortedOrder,
      sortedBy: this.sortedByField,
      filters: {},
      hydrate: {},
    };
  },
  watch: {
    filteredResults() {
      this.changeVisibility();
    },
  },
  computed: {
    tableIsEmpty() {
      return this.filteredResults && this.filteredResults.length === 0;
    },
    filterActions() {
      return this.actions;
    },
    filteredResults() {
      const matchSearch = (item) => {
        if (this.querySearch === undefined) {
          return true;
        }
        const querySearch = this.querySearch.toLowerCase();

        return item[this.searchOn]
          .toString()
          .toLowerCase()
          .includes(querySearch);
      };
      const matchFilters = (item) => {
        if (this.filters) {
          return Object.keys(this.filters).every((key) => {
            return this.filters[key].includes(item[key]);
          });
        }

        return true;
      };
      const itemComparator = (a, b) => {
        const modifier = this.sortedOrder === "desc" ? -1 : 1;

        if (a[this.sortedBy] < b[this.sortedBy]) return -1 * modifier;
        if (a[this.sortedBy] > b[this.sortedBy]) return 1 * modifier;

        return 0;
      };

      return this.data
        .filter(matchSearch)
        .filter(matchFilters)
        .sort(itemComparator);
    },
  },
  beforeMount() {
    this.sortedBy = this.sortedByField;

    return this.activeFilters
      .filter((filter) => filter.values.length)
      ?.forEach(({ column, values }) => {
        this.$set(this.filters, column, values);
      });
  },
  methods: {
    itemValue(item, column) {
      if (column.subfield) {
        return item[column.field][column.subfield];
      }
      return item[column.field];
    },
    onActionClicked(action, item) {
      this.$emit("onActionClicked", action, item);
    },
    sort(column) {
      this.$emit("sort-column", column.field, this.sortOrder);
      this.sortedBy = column.field;
      if (column.field === this.sortedBy) {
        this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
      }
    },
    onApplyFilters(column, selectedOptions) {
      if (selectedOptions.length) {
        this.$set(this.filters, column.field, selectedOptions);
      } else {
        this.$delete(this.filters, column.field);
      }
      this.$emit("filter-applied", {
        column: column.field,
        values: selectedOptions,
      });
    },
    changeVisibility() {
      const handleIntersection = (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            this.$set(this.hydrate, entry.target.id, true);
          }
        }
      };

      const observer = new IntersectionObserver(handleIntersection);

      this.data.forEach((item) => {
        const element = document.getElementById(item.id);
        if (!element) return;

        observer.observe(element);
      });
    },
  },
  mounted() {
    this.changeVisibility();
  },
};
</script>

<style lang="scss" scoped>
$headerColor: var(--bg-opacity-4);
$borderColor: var(--bg-opacity-6);

.table-info {
  $this: &;
  display: flex;
  flex-direction: column;
  padding: 0;
  min-height: 0;
  list-style: none;
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  &__header {
    border: 1px solid $borderColor;
    border-radius: var(--m, 10px) var(--m, 10px) 0px 0px;
    background: $headerColor;
    min-height: 49px;
    position: relative;
    margin-top: $base-space * 2;
    .table-info:has(.empty) & {
      border-bottom: 1px solid $borderColor;
    }
    .svg-icon {
      fill: var(--fg-secondary);
    }
    &__checkbox {
      margin: 0 !important;
    }
    &__button {
      position: absolute !important;
      top: 2em;
      right: 2em;
      margin-bottom: 0 !important;
    }
    #{$this}__item {
      border: unset;
      min-height: 50px;
      background: none;
      padding-top: 0.2em;
      padding-bottom: 0.2em;
      display: flex;
      align-items: center;
    }
    :deep(button) {
      color: var(--fg-primary);
      .svg-icon {
        fill: var(--fg-primary);
      }
    }
    button:not(.button) {
      cursor: pointer;
      border: 0;
      outline: none;
      background: transparent;
      padding-left: 0;
      padding-right: 0;
      @include font-size(14px);
      text-align: left;
      display: flex;
      align-items: center;
      @include media("<=desktop") {
        display: block;
        .svg-icon {
          display: block;
        }
      }
      span {
        white-space: nowrap;
      }
    }
  }
  &__body {
    overflow: auto;
    padding-bottom: 0.5em;
    min-height: 250px;
    @extend %hide-scrollbar;
    #{$this}__item {
      &:hover,
      &:focus {
        background: var(--bg-accent-grey-3);
      }
    }
  }
  &__item {
    position: relative;
    display: flex;
    align-items: center;
    background: var(--bg-accent-grey-1);
    color: var(--fg-secondary);
    list-style: none;
    padding: $base-space * 2 $base-space * 2;
    width: 100%;
    min-height: $base-space * 10;
    text-decoration: none;
    outline: none;
    border: 1px solid $borderColor;
    border-top: 0;

    &__col {
      text-align: left;
      margin-right: 1em;
      flex: 1 1 0px;
      &:nth-last-of-type(-n + 1) {
        max-width: 120px;
      }
      &:first-child {
        width: auto;
        min-width: auto;
        flex-grow: 2.5;
      }
      &.progress {
        min-width: 160px;
      }
    }
  }
  .empty {
    margin-top: 5em;
    height: auto;
    min-height: 50vh;
  }
  &__main {
    margin: 0;
    color: var(--fg-primary);
    .table-info__item:hover & {
      color: var(--fg-cuaternary);
    }
  }
  &__actions {
    display: flex;
    justify-content: flex-start;
    flex-direction: row;
    align-items: center;
    gap: $base-space;

    &__buttons {
      display: flex;
      flex-shrink: 0;
    }
    &__button {
      position: relative;
      display: inline-block;
      padding: $base-space;
      .svg-icon {
        margin: 0;
      }
      & + #{$this} {
        margin-left: auto;
      }
    }
  }
}
button[data-title] {
  position: relative;
  @extend %has-tooltip--top;
  @extend %tooltip-large-text;
}
</style>
