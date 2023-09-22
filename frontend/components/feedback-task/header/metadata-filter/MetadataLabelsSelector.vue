<template>
  <div class="labels-selector">
    <MetadataLabelsSelectorSearch
      v-model="searchText"
      placeholder="Filter by..."
      :selected-options="selectedOptions"
    />

    <BaseCheckbox
      class="labels-selector__item"
      v-for="option in labelsFilteredBySearchText"
      :key="option.label"
      :value="option.selected"
      v-model="option.selected"
    >
      {{ option.label }}
    </BaseCheckbox>
  </div>
</template>
<script>
export default {
  props: {
    metadata: {
      type: Object,
      required: true,
    },
  },
  data: () => {
    return {
      searchText: "",
    };
  },
  computed: {
    selectedOptions() {
      return this.metadata.options.filter((option) => option.selected);
    },
    labelsFilteredBySearchText() {
      return this.metadata.options.filter((option) =>
        option.label.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
  },
};
</script>
<style lang="scss" scoped>
.labels-selector {
  &__item {
    display: flex;
  }
}
</style>
