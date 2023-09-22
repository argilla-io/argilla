<template>
  <div class="labels-selector">
    <MetadataLabelsSelectorSearch
      v-model="searchText"
      placeholder="Filter by..."
      :selected-labels="selectedLabels"
      @remove-label="removeSelectedLabel"
    />
    <BaseCheckbox
      class="labels-selector__item"
      v-for="label in labelsFilteredBySearchText"
      :key="label"
      :id="label"
      :ref="label"
      v-model="selected"
      :value="label"
    >
      {{ label }}
    </BaseCheckbox>
  </div>
</template>
<script>
export default {
  props: {
    labels: {
      type: Array,
      required: true,
    },
    selectedLabels: {
      type: Array,
      required: true,
    },
  },
  data: () => {
    return {
      searchText: "",
    };
  },
  model: {
    prop: "selectedLabels",
    event: "input",
  },
  computed: {
    selected: {
      get() {
        return this.selectedLabels;
      },
      set(newValue) {
        this.$emit("input", newValue);
      },
    },
    labelsFilteredBySearchText() {
      return this.labels.filter((label) =>
        label.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
  },
  methods: {
    removeSelectedLabel(label) {
      const selectedLabels = this.selectedLabels.filter((l) => l !== label);
      this.$emit("input", selectedLabels);
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
