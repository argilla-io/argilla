<template>
  <div
    class="labels-selector"
    @keyup.enter="includePreselectedOption"
    @keyup.up="preselectPreviousOption"
    @keyup.down="preselectNextOption"
  >
    <BaseSearch v-model="searchText" :placeholder="$t('search')" />
    <div class="labels-selector__items">
      <BaseCheckbox
        class="labels-selector__item"
        :class="
          index === preSelectionIndex
            ? 'labels-selector__item--highlighted'
            : null
        "
        v-for="(
          { name, numberOfDatasets }, index
        ) in workspacesFilteredBySearchText"
        :key="name"
        :value="selectedWorkspaces.includes(name)"
        @change="toggleSelectedOption(name)"
        @mouseover.native="preSelectionIndex = index"
      >
        {{ name }}
        <span class="labels-selector__number">({{ numberOfDatasets }})</span>
      </BaseCheckbox>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    workspaces: {
      type: Array,
      required: true,
    },
    selectedWorkspaces: {
      type: Array,
      required: true,
    },
  },
  model: {
    prop: "selectedWorkspaces",
    event: "input",
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
  },
  computed: {
    workspacesFilteredBySearchText() {
      return this.workspaces.filter((workspace) =>
        workspace.name.toLowerCase().includes(this.searchText.toLowerCase())
      );
    },
    workspacesLength() {
      return this.workspaces.length;
    },
  },
  methods: {
    includePreselectedOption() {
      if (!this.workspacesFilteredBySearchText.length) return;

      this.toggleSelectedOption(
        this.workspacesFilteredBySearchText[this.preSelectionIndex]
      );

      this.preSelectionIndex = 0;
    },
    toggleSelectedOption(workspace) {
      const index = this.selectedWorkspaces.indexOf(workspace);
      if (index === -1) {
        this.selectedWorkspaces.push(workspace);
      } else {
        this.selectedWorkspaces.splice(index, 1);
      }
    },
    preselectNextOption() {
      this.preSelectionIndex === this.workspacesLength - 1
        ? (this.preSelectionIndex = 0)
        : this.preSelectionIndex++;
    },
    preselectPreviousOption() {
      this.preSelectionIndex === 0
        ? (this.preSelectionIndex = this.workspacesLength - 1)
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
  &__number {
    @include font-size(12px);
  }
}
</style>
