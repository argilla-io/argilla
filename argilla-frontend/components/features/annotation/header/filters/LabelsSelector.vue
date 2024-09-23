<template>
  <div
    class="labels-selector"
    @keyup.enter="includePreselectedOption"
    @keyup.up="preselectPreviousOption"
    @keyup.down="preselectNextOption"
  >
    <LabelsSelectorSearch
      v-model="searchText"
      :placeholder="$t('filterBy')"
      :selected-options="filter.selectedOptions"
    />
    <OptionsSelector
      class="labels-selector__operator"
      v-if="filter.hasOperator"
      v-model="filter.operator"
      :options="['and', 'or']"
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
        :key="option.value"
        :value="option.selected"
        v-model="option.selected"
        @mouseover.native="preSelectionIndex = index"
      >
        {{ option.text ?? option.value }}
      </BaseCheckbox>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    filter: {
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
    filterOptions: {
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
      return this.filter.filterByText(this.searchText);
    },
    optionsLength() {
      return this.filter.options.length;
    },
    filterOptions() {
      return this.filter.options;
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
  &__items {
    max-height: 200px;
    overflow: auto;
    margin-top: $base-space;
  }
  &__item {
    &.checkbox {
      display: flex;
      padding: 6px $base-space;
      border-radius: $border-radius;
    }
    &--highlighted {
      background: var(--bg-opacity-4);
    }
    :deep(.checkbox__container) {
      background: none !important;
      border: 0 !important;
    }
    :deep(label) {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    &.checkbox :deep(.checkbox__container .svg-icon) {
      fill: var(--fg-cuaternary);
      min-width: 16px;
    }
  }
  &__operator {
    margin-top: $base-space;
  }
}
</style>
