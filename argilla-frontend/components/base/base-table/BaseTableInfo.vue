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
    <div class="table-info">
      <div class="table-info__header">
        <slot name="columns">
          <div class="table-info__item">
            <div
              v-for="(column, key) in columns"
              :key="key"
              :class="[`table-info__item__col`, column.class]"
            >
              <lazy-table-filtrable-column
                :column="column"
                :data="data"
                :filters="filters"
                v-if="column.filtrable"
                @applyFilters="onApplyFilters"
              />
              <button
                v-else-if="column.sortable"
                :data-title="column.tooltip"
                :class="[sortOrder, { active: sortedBy === column.field }]"
                @click="sort(column)"
              >
                <svgicon width="18" height="18" color="#4D4D4D" name="sort" />
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
        <div class="table-info__body">
          <ul>
            <li v-for="item in filteredResults" :key="String(item.id)">
              <div class="table-info__item">
                <span
                  v-for="(column, idx) in columns"
                  :key="idx"
                  :class="[`table-info__item__col`, column.class]"
                >
                  <span :class="column.class">
                    <span v-if="column.type === 'action'">
                      <div class="table-info__actions">
                        <nuxt-link v-if="item.link" :to="item.link"
                          >{{ itemValue(item, column) }}
                        </nuxt-link>
                        <span v-else>{{ itemValue(item, column) }}</span>
                        <div class="table-info__actions__buttons">
                          <base-action-tooltip
                            v-for="action in column.actions"
                            :key="action.name"
                            :tooltip="action.tooltip"
                          >
                            <base-button
                              :title="action.title"
                              class="table-info__actions__button button-icon"
                              @click="onActionClicked(action.name, item)"
                            >
                              <svgicon
                                v-if="action.icon !== undefined"
                                :name="action.icon"
                                width="16"
                                height="16"
                              />
                            </base-button>
                          </base-action-tooltip>
                        </div>
                      </div>
                    </span>
                    <span v-else-if="column.type === 'progress'">
                      <DatasetProgress :dataset="item" />
                    </span>
                    <base-date
                      format="date-relative-now"
                      v-else-if="column.type === 'date'"
                      :date="itemValue(item, column)"
                    />
                    <span v-else>{{ itemValue(item, column) }}</span>
                  </span>
                </span>
              </div>
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
  },
  data() {
    return {
      sortOrder: this.sortedOrder,
      sortedBy: this.sortedByField,
      filters: {},
    };
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
  },
};
</script>

<style lang="scss" scoped>
.table-info {
  $this: &;
  display: flex;
  flex-direction: column;
  padding: 0;
  min-height: 0;
  list-style: none;
  color: $black-54;
  ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  &__header {
    background: palette(white);
    min-height: 50px;
    position: relative;
    margin-top: $base-space * 2;
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
      min-height: 50px;
      background: none;
      padding-top: 0.2em;
      padding-bottom: 0.2em;
      display: flex;
      align-items: center;
    }
    button:not(.button) {
      cursor: pointer;
      border: 0;
      outline: none;
      background: transparent;
      padding-left: 0;
      padding-right: 0;
      color: $black-87;
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
        background: #fcfcfc;
      }
    }
  }
  &__item {
    position: relative;
    display: flex;
    align-items: center;
    background: palette(white);
    list-style: none;
    padding-inline: $base-space * 3 $base-space * 8;
    width: 100%;
    min-height: $base-space * 10;
    text-decoration: none;
    outline: none;
    border: 1px solid palette(grey, 700);
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
        flex-grow: 1.5;
      }
      &.progress {
        min-width: 160px;
      }
    }
    .svg-icon {
      margin-right: $base-space;
      fill: $black-54;
      &:hover {
        fill: $black-87;
      }
    }
  }
  .empty {
    margin-top: 5em;
    height: auto;
  }
  &__actions {
    display: flex;
    justify-content: flex-start;
    flex-direction: row;
    align-items: center;
    gap: $base-space;

    &__buttons {
      display: flex;

      &__button {
        position: relative;
        display: inline-block;
        .svg-icon {
          margin: 0;
        }
        & + #{$this} {
          margin-left: auto;
        }
      }
    }
  }
  &__title {
    display: block;
    hyphens: auto;
    word-break: break-word;
    .button-icon {
      padding: $base-space;
      display: inline-block;
      .svg-icon {
        margin: 0;
      }
    }
    a {
      text-decoration: none;
      &:hover {
        color: palette(black);
      }
    }
  }
  .text {
    color: $black-54;
    p {
      display: inline-block;
      background: palette(grey, 800);
      padding: 0.5em;
      border-radius: 10px;
      margin-right: 0.5em;
      margin-top: 0;
      hyphens: auto;
      word-break: break-word;
      &:last-child {
        margin-bottom: 0;
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
