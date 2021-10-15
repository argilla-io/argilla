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
  <div>
    <SortFilter
      v-for="index in numberOfSortFields"
      :key="index"
      class="sort"
      :selected-field="selectedFields[index - 1]"
      :sort-options="filteredSortOptions"
      @removeSortField="onRemoveSortField(index)"
      @addSortField="onAddSortField(index, ...arguments)"
    />
    <a
      v-if="selectedFields.length === numberOfSortFields"
      class="sort__add-button"
      href="#"
      @click="addNewField"
      >+ Add another field</a
    >
    <div class="sort__buttons" v-if="sort.length || selectedFields.length">
      <re-button
        class="button-tertiary--small button-tertiary--outline"
        @click="cancel"
        >Cancel</re-button
      >
      <re-button class="button-primary--small" @click="apply">Filter</re-button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    sortOptions: {
      type: Array,
      required: true,
    },
    sort: {
      type: Array,
    },
  },
  data: () => {
    return {
      numberOfSortFields: 1,
      selectedFields: [],
    };
  },
  computed: {
    filteredSortOptions() {
      return this.sortOptions.filter(
        (opt) =>
          !this.selectedFields.some((field) => opt.id.toString() === field.id)
      );
    },
  },
  mounted() {
    this.numberOfSortFields = this.sort.length === 0 ? 1 : this.sort.length;
    this.selectedFields = [...this.sort];
  },
  methods: {
    addNewField() {
      this.numberOfSortFields += 1;
    },
    onRemoveSortField(index) {
      this.selectedFields.splice(index - 1, 1);
      if (this.numberOfSortFields > 1) {
        this.numberOfSortFields -= 1;
      }
    },
    onAddSortField(index, option, direction) {
      const item = {
        ...option,
        id:
          option.group.toLowerCase() === "metadata"
            ? "metadata." + option.key
            : option.key,
        name: option.name,
        order: direction,
      };
      this.selectedFields.splice(index - 1, 1, item);
    },
    apply() {
      this.$emit("sortBy", this.selectedFields);
    },
    cancel() {
      this.$emit("closeSort");
    },
  },
};
</script>

<style lang="scss" scoped>
.sort {
  margin-bottom: 0.5em;
  &__buttons {
    display: flex;
    margin-top: 1.5em;
    & > * {
      display: block;
      width: 100%;
      margin-right: 0.5em;
      min-height: 38px;
      &:last-child {
        margin-right: 0;
      }
    }
  }
  &__add-button {
    @include font-size(13px);
    margin-top: 1em;
    color: $primary-color;
    outline: none;
    text-decoration: none;
    display: block;
  }
}
</style>
