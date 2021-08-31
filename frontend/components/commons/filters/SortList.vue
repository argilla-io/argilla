<template>
    <div>
      <SortFilter @removeSortField="onRemoveSortField(index)" @addSortField="onAddSortField(index, ...arguments)" class="sort" v-for="index in numberOfSortFields" :selectedField="selectedFields[index - 1]" :sortOptions="filteredSortOptions" :key="index"/>
      <a v-if="selectedFields.length === numberOfSortFields" class="sort__add-button" href="#" @click="addNewField">add field +</a>
      <re-button v-if="selectedFields.length" class="discarded sort__button button-primary--small" @click="apply()">Apply</re-button>
    </div>
</template>

<script>
export default {
  data: () => {
    return {
      numberOfSortFields: 1,
      selectedFields: []
    }
  },
  props: {
    sortOptions: {
      type: Array,
      required: true
    }
  },
  computed: {
    filteredSortOptions() {
      return this.sortOptions.filter(opt => !this.selectedFields.some((field) => opt.id.toString() === field.id));
    }
  },
  methods: {
    addNewField() {
      this.numberOfSortFields += 1
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
        id: option.id,
        name: option.name,
        direction: direction,
      }
      this.selectedFields.splice(index - 1, 1, item);
    },
    apply() {
      console.log(this.selectedFields)
    }
  }
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

