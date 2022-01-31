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
              class="table-info__item__col"
            >
              <button
                :data-title="column.tooltip"
                v-if="!column.hidden"
                :class="[sortOrder, { active: sortedBy === column.field }]"
                @click="sort(column)"
              >
                {{ column.name }}
                <svgicon
                  color="#4C4EA3"
                  width="7"
                  height="7"
                  :name="
                    sortedBy === column.field && sortOrder === 'desc'
                      ? 'chev-top'
                      : 'chev-bottom'
                  "
                />
              </button>
            </div>
          </div>
        </slot>
      </div>
      <ResultsEmpty
        v-if="!data.length"
        :title="noDataInfo.title"
        :message="noDataInfo.message"
        :icon="noDataInfo.icon"
      />
      <template v-else-if="resultsAvailable">
        <div v-for="group in groups" :key="group" class="table-info__body">
          <span v-if="groupBy && groupBy !== 'list'" class="table-info__group">
            <p class="table-info__group__title">
              {{ group }}
            </p>
          </span>
          <ul>
            <li
              v-for="item in filteredResultsByGroup(group)"
              :key="String(item.id)"
            >
              <div class="table-info__item">
                <!-- <ReCheckbox v-if="globalActions" v-model="item.selectedRecord" class="list__item__checkbox" :value="item.name" @change="onCheckboxChanged($event, item.id, key)" /> -->
                <span
                  v-for="(column, idx) in columns"
                  :key="idx"
                  class="table-info__item__col"
                >
                  <span :class="column.class">
                    <a
                      v-if="column.type === 'action'"
                      href="#"
                      @click.prevent="onActionClicked(item.kind, item)"
                      >{{ itemValue(item, column) }}
                    </a>
                    <span v-else-if="column.type === 'link'">
                      <NuxtLink v-if="item.link" :to="item.link"
                        >{{ itemValue(item, column) }}
                      </NuxtLink>
                      <span v-else>{{ itemValue(item, column) }}</span>
                      <re-action-tooltip tooltip="Copied">
                        <ReButton
                          title="Copy to clipboard"
                          class="table-info__actions__button button-icon"
                          @click.prevent="onActionClicked('copy-name', item)"
                        >
                          <svgicon name="copy" width="12" height="13" />
                        </ReButton>
                      </re-action-tooltip>
                    </span>
                    <ReDate
                      v-else-if="column.type === 'date'"
                      :date="itemValue(item, column)"
                    />
                    <span v-else-if="column.type === 'number'">
                      {{ itemValue(item, column) | formatNumber }}
                    </span>
                    <span
                      v-else-if="
                        !isNaN(itemValue(item, column)) &&
                        column.type === 'percentage'
                      "
                    >
                      {{ itemValue(item, column) | percent }}
                    </span>
                    <span v-else-if="column.type === 'object'">
                      <p
                        v-for="key in Object.keys(itemValue(item, column))"
                        :key="key"
                      >
                        <strong>{{ key }}:</strong>
                        {{ itemValue(item, column)[key] }}
                      </p>
                    </span>
                    <!-- TODO: remove references to task -->
                    <span v-else-if="column.type === 'task'">
                      {{ itemValue(item, column) }}
                      <span
                        v-if="itemValue(item, column) === 'Text2Text'"
                        class="table-info__tag"
                        >Experimental</span
                      >
                    </span>
                    <span v-else>{{ itemValue(item, column) }}</span>
                  </span>
                </span>
                <div v-if="visibleActions" class="table-info__actions">
                  <re-action-tooltip
                    v-for="action in filterActions"
                    :key="action.index"
                    :tooltip="action.tooltip"
                  >
                    <ReButton
                      :title="action.title"
                      class="table-info__actions__button button-icon"
                      @click="onActionClicked(action.name, item)"
                    >
                      <svgicon
                        v-if="action.icon !== undefined"
                        :name="action.icon"
                        width="12"
                        height="13"
                      />
                    </ReButton>
                  </re-action-tooltip>
                </div>
                <ReModal
                  :modal-custom="true"
                  :prevent-body-scroll="true"
                  modal-class="modal-secondary"
                  :modal-visible="visibleModalId === item.id"
                  modal-position="modal-center"
                  @close-modal="$emit('close-modal')"
                >
                  <div>
                    <p class="modal__title">{{ deleteModalContent.title }}</p>
                    <p v-html="deleteModalContent.text"></p>
                    <div class="modal-buttons">
                      <ReButton
                        class="button-tertiary--small button-tertiary--outline"
                        @click="$emit('close-modal')"
                      >
                        Cancel
                      </ReButton>
                      <ReButton
                        class="button-secondary--small"
                        @click="onActionClicked('confirm-delete', item)"
                      >
                        Yes, delete
                      </ReButton>
                    </div>
                  </div>
                </ReModal>
              </div>
            </li>
          </ul>
          <!-- <ReModal :modal-custom="true" :prevent-body-scroll="true" modal-class="modal-primary" :modal-visible="visibleModalId === 'all'" modal-position="modal-center" @close-modal="$emit('close-modal')">
            <div>
              <p class="modal__title">Delete confirmation</p>
              <span>
                You are about to delete: <br />
                <span v-for="item in selectedItems" :key="item.id">
                  <strong>{{ item.actionName }}</strong><br /></span>
              </span>
              <p>This process cannot be undone</p>
              <br />
              <div class="modal-buttons">
                <ReButton class="button-tertiary--small button-tertiary--outline" @click="$emit('close-modal')">
                  Cancel
                </ReButton>
                <ReButton class="button-primary--small" @click="$emit('delete-multiple')">
                  Yes, delete
                </ReButton>
              </div>
            </div>
          </ReModal> -->
        </div>
      </template>
      <ResultsEmpty v-else :title="emptySearchInfo.title" />
    </div>
  </transition>
</template>

<script>
import "assets/icons/delete";
import "assets/icons/refresh";
import "assets/icons/copy";
import "assets/icons/copy-url";
import "assets/icons/datasource";
import "assets/icons/chev-top";
import "assets/icons/chev-bottom";
export default {
  props: {
    data: {
      type: Array,
      default: () => [],
    },
    actions: {
      type: Array,
      default: () => [],
    },
    columns: Array,
    searchOn: {
      type: String,
      default: undefined,
    },
    sortedOrder: {
      type: String,
      default: "desc",
    },
    sortedByField: {
      type: String,
      default: undefined,
    },
    noDataInfo: {
      title: undefined,
      message: undefined,
      icon: undefined,
    },
    emptySearchInfo: {
      title: undefined,
      description: undefined,
      icon: undefined,
    },
    hideButton: {
      type: Boolean,
      default: false,
    },
    visibleModalId: {
      type: String | Array,
      default: undefined,
    },
    deleteModalContent: {
      type: Object,
    },
    globalActions: {
      type: Boolean,
      default: true,
    },
    groupBy: {
      type: String,
      default: undefined,
    },
    querySearch: {
      type: String,
      default: undefined,
    },
  },
  data() {
    return {
      sortOrder: this.sortedOrder,
      visibleActions: true,
      sortedBy: this.sortedByField,
      allRecordsSelected: false,
      selectedItems: [],
    };
  },
  computed: {
    resultsAvailable() {
      return this.filteredResults.length !== 0;
    },
    dataSchema() {
      if (this.data && this.data.length > 0) {
        return Object.keys(this.data[0]);
      }
      return [];
    },
    filterActions() {
      return this.actions.filter((a) => a.hide !== this.hideButton);
    },
    filteredResults() {
      const matchSearch = (item) => {
        if (this.querySearch === undefined) {
          return true;
        }
        const querySearch = this.querySearch.toLowerCase();
        if (this.searchOn) {
          return item[this.searchOn]
            .toString()
            .toLowerCase()
            .includes(querySearch);
        }
        return false;
      };
      const itemComparator = (a, b) => {
        let modifier = 1;
        if (this.sortedOrder === "desc") modifier = -1;
        if (a[this.sortedBy] < b[this.sortedBy]) return -1 * modifier;
        if (a[this.sortedBy] > b[this.sortedBy]) return 1 * modifier;
        return 0;
      };
      const results = this.data.filter(matchSearch);
      return results.sort(itemComparator);
    },
    groups() {
      if (this.groupBy) {
        let filtergroups = [];
        this.filteredResults.forEach((result) => {
          filtergroups.push(result[this.groupBy]);
        });
        filtergroups = [...new Set(filtergroups)];
        return filtergroups;
      }
      return 1;
    },
  },
  beforeMount() {
    this.sortedBy = this.sortedByField;
  },
  mounted() {
    this.filteredResults.forEach((r) => {
      const rec = r;
      rec.selectedRecord = false;
    });
  },
  methods: {
    itemDisabled(item) {
      if (item.status) {
        return item.status.toLowerCase() !== "ready";
      }
      return undefined;
    },
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
    filteredResultsByGroup(group) {
      if (this.groupBy) {
        return this.filteredResults.filter(
          (item) => item[this.groupBy] === group
        );
      }
      return this.filteredResults;
    },
    selectAll(value) {
      this.onAllCheckboxChanged(value);
    },
    onAllCheckboxChanged(value) {
      this.filteredResults.forEach((r) => {
        const rec = r;
        rec.selectedRecord = value;
      });
      this.selectedItems = this.filteredResults.filter(
        (f) => f.selectedRecord === true
      );
    },
    onCheckboxChanged(value, id) {
      this.filteredResults.forEach((r) => {
        if (r.id === id) {
          const rec = r;
          rec.selectedRecord = value;
        }
      });
      if (
        this.filteredResults.some(
          (f) => f.selectedRecord === false || undefined
        )
      ) {
        this.allRecordsSelected = false;
      } else {
        this.allRecordsSelected = true;
      }
      this.selectedItems = this.filteredResults.filter(
        (f) => f.selectedRecord === true
      );
    },
  },
};
</script>

<style lang="scss" scoped>
.table-info {
  $this: &;
  padding: 0;
  list-style: none;
  margin-bottom: 5em;
  ul {
    background: $lighter-color;
    list-style: none;
    padding: 0;
    margin: 0;
  }
  li {
    &:hover,
    &:focus {
      background: #fcfcfc;
    }
  }
  &__header {
    background: $lighter-color;
    min-height: auto;
    position: relative;
    padding-bottom: 0.3em;
    margin-top: 1em;
    margin-bottom: 3px;
    padding: 1em 0;
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
      min-height: auto;
      background: none;
      border-bottom: none;
      padding-top: 0;
      padding-bottom: 0.2em;
      // &:hover {
      //   background:transparent ;
      // }
    }
    button:not(.re-button) {
      cursor: pointer;
      border: 0;
      outline: none;
      background: transparent;
      padding-left: 0;
      padding-right: 0;
      color: $font-secondary;
      @include font-size(14px);
      font-family: $sff;
      .svg-icon {
        margin-left: 0.5em;
      }
    }
  }
  &__body {
    overflow: auto;
    height: calc(100vh - 203px);
    padding-bottom: 0.5em;
  }
  &__item {
    position: relative;
    list-style: none;
    padding: 2em 8em 2em 2em;
    display: flex;
    width: 100%;
    border-bottom: 1px solid $line-light-color;
    align-items: flex-start;
    text-decoration: none;
    outline: none;
    &__col {
      text-align: left;
      margin-right: 1.5em;
      flex: 1 1 0px;
      // text-overflow: ellipsis;
      // overflow: hidden;
      &:nth-last-of-type(-n + 2) {
        max-width: 120px;
      }
      &:nth-last-of-type(3) {
        max-width: 180px;
      }
      &:nth-of-type(2) {
        min-width: 30%;
      }
      // .task span {
      //   display: flex;
      // }
      &:first-child {
        flex-shrink: 0;
        min-width: 220px;
      }
    }
    .svg-icon {
      margin-right: 1em;
      fill: $font-medium-color;
    }
  }
  &__tag {
    background: palette(grey, dark);
    display: inline-block;
    border-radius: 3px;
    color: $lighter-color;
    @include font-size(12px);
    box-shadow: 0 1px 4px 1px rgba(222, 222, 222, 0.5);
    padding: 0.1em 0.5em;
    margin-left: 1em;
  }
  .empty {
    margin-top: 5em;
    height: auto;
  }
  // &__item:not(.disabled) {
  //   &:hover,
  //   &:focus {
  //     background: $line-lighter-color;
  //     #{$this}__header & {
  //       background: transparent;
  //     }
  //   }
  // }
  &__actions {
    position: absolute;
    right: 2em;
    &__button {
      position: relative;
      margin-left: 2em;
      padding: 0 !important;
      .svg-icon {
        fill: palette(grey, dark);
        margin-right: 0;
      }
      & + #{$this} {
        margin-left: auto;
      }
    }
  }
  &__title {
    display: block;
    @include font-size(15px);
    word-break: break-word;
    display: flex;
    align-items: center;
    .button-icon {
      margin-left: 5px;
      padding: 0;
      margin-bottom: 2px;
      .svg-icon {
        fill: $font-medium-color;
      }
    }
    a {
      width: 100%;
      text-decoration: none;
      &:hover {
        color: $primary-color;
      }
    }
  }
  &__group {
    padding-bottom: 2em;
    border-bottom: 1px solid $line-smooth-color;
    display: block;
    &__title {
      margin: 3em 0 0 0;
      font-weight: 600;
      .svg-icon {
        margin-right: 1em;
      }
    }
  }
  .model {
    color: $font-dark-color;
    border: 1px solid $line-smooth-color;
    border-radius: 3px;
    padding: 0.1em 2em;
    display: inline-block;
    max-width: 280px;
    font-weight: 600;
    word-break: break-word;
  }
  .text {
    color: $font-medium-color;
    p {
      display: inline-block;
      background: palette(grey, bg);
      padding: 0.5em;
      border-radius: 10px;
      margin-right: 0.5em;
      margin-top: 0;
      word-break: break-all;
      &:last-child {
        margin-bottom: 0;
      }
    }
  }
  .dataSource {
    color: $font-medium-color;
    font-weight: 600;
    white-space: nowrap;
  }
  .actionName {
    margin-left: 1em;
    display: inline-block;
  }
  .metrics {
    display: block;
    span {
      display: inline-block;
      padding: 0.2em 0.5em;
      margin-top: 1em;
      background: lighten($secondary-color, 44%);
      margin-right: 3px;
      border-radius: 2px;
    }
  }
}
.--show-tooltip {
  @extend %activetooltip;
  @extend %tooltip--left;
}
$color: #333346;
button[data-title] {
  position: relative;
  @extend %hastooltip;
  &:after {
    padding: 0.5em 1em;
    bottom: 100%;
    right: 50%;
    transform: translateX(50%);
    background: $color;
    color: white;
    border: none;
    border-radius: 3px;
    @include font-size(14px);
    font-weight: 600;
    margin-bottom: 0.5em;
    min-width: 220px;
    white-space: break-spaces;
  }
  &:before {
    right: calc(50% - 7px);
    top: -0.5em;
    border-top: 7px solid $color;
    border-right: 7px solid transparent;
    border-left: 7px solid transparent;
  }
}
</style>
