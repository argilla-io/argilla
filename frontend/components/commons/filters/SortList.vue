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
      >add field +</a
    >
    <re-button
      v-if="selectedFields.length"
      class="discarded sort__button button-primary--small"
      @click="apply"
      >Apply</re-button
    >
  </div>
</template>

<script>
export default {
  props: {
    sortOptions: {
      type: Array,
      required: true,
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
  methods: {
    addNewField() {
      this.numberOfSortFields += 1;
    },
    onRemoveSortField(index) {
      this.selectedFields.splice(index - 1, 1);
      if (this.numberOfSortFields > 1) {
        this.numberOfSortFields -= 1;
      }
      this.apply();
    },
    onAddSortField(index, option, direction) {
      const item = {
        id: option.group == "Metadata" ? "metadata." + option.id : option.id,
        name: option.name,
        order: direction,
      };
      this.selectedFields.splice(index - 1, 1, item);
    },
    apply() {
      this.$emit("sortBy", this.selectedFields);
    },
  },
};
</script>

<style lang="scss" scoped>
.sort {
  margin-bottom: 0.5em;
  &__button {
    margin-left: auto;
    margin-right: 0;
    margin-bottom: 0;
  }
  &__add-button {
    margin-top: 1em;
    color: $primary-color;
    outline: none;
    text-decoration: none;
    display: block;
  }
}
</style>
