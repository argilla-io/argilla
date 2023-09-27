<template>
  <div
    class="labels-selector"
    @keyup.enter="includePreselectedOption"
    @keyup.up="preselectPreviousOption"
    @keyup.down="preselectNextOption"
  >
    <MetadataLabelsSelectorSearch
      v-model="searchText"
      :placeholder="$t('filterBy')"
      :selected-options="metadata.selectedOptions"
    />
    <div class="labels-selector__items">
      <BaseCheckbox
        class="labels-selector__item"
        :class="
          index === preSelectionIndex
            ? 'labels-selector__item--highlighted'
            : null
        "
        v-for="(option, index) in labelsFilteredBySearchText"
        :key="option.label"
        :value="option.selected"
        v-model="option.selected"
        @mouseover.native="preSelectionIndex = index"
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
      preSelectionIndex: 0,
    };
  },
  watch: {
    searchText() {
      this.preSelectionIndex = 0;
    },
    metadataOptions: {
      handler: function () {
        if (this.searchText.length) {
          this.searchText = "";
        }
      },
      deep: true,
    },
  },
  computed: {
    labelsFilteredBySearchText() {
      return this.metadata.filterByText(this.searchText);
    },
    optionsLength() {
      return this.metadata.options.length;
    },
    metadataOptions() {
      return this.metadata.options;
    },
  },
  methods: {
    includePreselectedOption() {
      if (!this.labelsFilteredBySearchText.length) return;

      this.toggleSelectedOption(
        this.labelsFilteredBySearchText[this.preSelectionIndex]
      );

      this.preSelectionIndex = 0;
    },
    toggleSelectedOption(option) {
      option.selected = !option.selected;
    },
    preselectNextOption() {
      this.preSelectionIndex === this.optionsLength - 1
        ? (this.preSelectionIndex = 0)
        : this.preSelectionIndex++;
    },
    preselectPreviousOption() {
      this.preSelectionIndex === 0
        ? (this.preSelectionIndex = this.optionsLength - 1)
        : this.preSelectionIndex--;
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
    overflow: auto;
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
      fill: $primary-color;
      min-width: 16px;
    }
  }
}
</style>
