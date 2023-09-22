<template>
  <div class="labels-selector">
    <MetadataLabelsSelectorSearch
      v-model="searchText"
      placeholder="Filter by..."
      :selected-options="metadata.selectedOptions"
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
    labelsFilteredBySearchText() {
      return this.metadata.filterByText(this.searchText);
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
