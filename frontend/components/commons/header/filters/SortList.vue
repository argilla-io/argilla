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
    <div class="filters--scrollable">
      <SortFilter
        v-for="index in numberOfSortFields"
        :key="index"
        class="sort"
        :selected-field="selectedFields[index - 1]"
        :sort-options="filteredSortOptions"
        @removeSortField="onRemoveSortField(index)"
        @addSortField="onAddSortField(index, ...arguments)"
      />
    </div>
    <base-button
      v-if="selectedFields.length === numberOfSortFields"
      class="sort__add-button link"
      @click="addNewField"
      >+ Add another field</base-button
    >
    <div class="sort__buttons" v-if="sort.length || selectedFields.length">
      <base-button class="primary outline" @click="cancel">Cancel</base-button>
      <base-button class="primary" @click="apply">Sort</base-button>
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
      const formatOptions = this.sortOptions.map((opt) => {
        if (opt.group.toLowerCase() === "metadata") {
          return {
            ...opt,
            id: `metadata.${opt.name}`,
            name: `Metadata.${opt.name}`,
          };
        }
        return opt;
      });
      return formatOptions.filter(
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
      if (this.selectedFields.length === 1) {
        this.$emit("sortBy", []);
      } else {
        this.selectedFields.splice(index - 1, 1);
      }
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
  margin-bottom: 1em;
  &__buttons {
    display: flex;
    margin-top: 1.5em;
    margin-bottom: 10px;
    & > * {
      display: block;
      width: 100%;
      &:last-child {
        margin-left: $base-space;
      }
    }
  }
  &__add-button {
    margin-top: 1em;
  }
}
</style>
