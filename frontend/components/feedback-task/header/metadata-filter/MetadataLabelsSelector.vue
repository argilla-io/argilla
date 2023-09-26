<template>
  <div
    class="labels-selector"
    @keyup.enter="includePreselectedOption"
    @keyup.up="preselectPreviousOption"
    @keyup.down="preselectNextOption"
  >
    <MetadataLabelsSelectorSearch
      v-model="searchText"
      placeholder="Filter by..."
      :selected-options="metadata.selectedOptions"
    />
    <div class="labels-selector__items">
      <BaseCheckbox
        class="labels-selector__item"
        :class="
          index === preselectionIndex
            ? 'labels-selector__item--highlighted'
            : null
        "
        v-for="(option, index) in labelsFilteredBySearchText"
        :key="option.label"
        :value="option.selected"
        v-model="option.selected"
        @mouseover.native="preselectionIndex = index"
      >
        {{ option.label }}
      </BaseCheckbox>
    </div>
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
      preselectionIndex: 0,
    };
  },
  watch: {
    searchText() {
      this.preselectionIndex = 0;
    },
  },
  computed: {
    labelsFilteredBySearchText() {
      return this.metadata.filterByText(this.searchText);
    },
    optionsLength() {
      return this.metadata.options.length;
    },
  },
  methods: {
    includePreselectedOption() {
      if (!this.labelsFilteredBySearchText.length) {
        return;
      }
      this.toggleSelectedOption(
        this.labelsFilteredBySearchText[this.preselectionIndex]
      );
      this.preselectionIndex = 0;
    },
    removeSelectedOption(option) {
      option.selected = false;
    },
    includeSelectedOption(option) {
      option.selected = true;
    },
    toggleSelectedOption(option) {
      if (option.selected) {
        this.removeSelectedOption(option);
      } else {
        this.includeSelectedOption(option);
      }
    },
    labelIsHighlighted(index) {
      return this.activedSearchWithResults && index === 0;
    },
    preselectNextOption() {
      this.preselectionIndex === this.optionsLength - 1
        ? (this.preselectionIndex = 0)
        : this.preselectionIndex++;
    },
    preselectPreviousOption() {
      this.preselectionIndex === 0
        ? (this.preselectionIndex = this.optionsLength - 1)
        : this.preselectionIndex--;
    },
  },
};
</script>
<style lang="scss" scoped>
.labels-selector {
  display: flex;
  flex-direction: column;
  margin-bottom: $base-space;
  &__items {
    max-height: 200px;
    overflow: scroll;
    margin-top: $base-space;
  }
  &__item {
    &.re-checkbox {
      display: flex;
      padding: calc($base-space / 2) $base-space;
      border-radius: $border-radius;
    }
    &--highlighted {
      background: $black-4;
    }
    :deep(.checkbox-container) {
      background: none !important;
      border: 0 !important;
    }
    :deep(label) {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    &.re-checkbox :deep(.checkbox-container .svg-icon) {
      fill: grey;
      min-width: 16px;
    }
  }
}
</style>
