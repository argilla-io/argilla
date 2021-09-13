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
    <div class="sort__buttons">
      <re-button
        class="button-tertiary--small button-tertiary--outline"
        @click="cancel"
        >Cancel</re-button
      >
      <re-button class="button-primary--small" @click="apply">Apply</re-button>
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
            ? "metadata." + option.id
            : option.id,
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
    button {
      margin-bottom: 0;
    }
    button:first-child {
      margin-left: auto;
      margin-right: 0.5em;
    }
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
