<template>
  <filter-dropdown
    class="dropdown"
    :visible="showDropdown"
    @visibility="toggleDropdown"
  >
    <template #dropdown-header>
      <span class="dropdown__text">Annotate as...</span>
    </template>
    <template #dropdown-content>
      <div class="dropdown-content">
        <SelectOptionsSearch
          allow-clear
          @clear="resetSearchText"
          v-model="searchText"
          placeholder="Search label..."
        />
        <div class="form" v-if="isInputsNotEmpty && showDropdown">
          <BulkAnnotationFormComponent
            :inputs="filteredInputs"
            :key="searchText"
            @on-submit="updateAnnotations"
          />
        </div>

        <div class="no-inputs-text" v-else>
          <span>0 results</span>
        </div>
      </div>
    </template>
  </filter-dropdown>
</template>

<script>
export default {
  name: "BulkAnnotation",
  props: {
    inputs: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      showDropdown: false,
      searchText: null,
    };
  },
  computed: {
    filteredInputs() {
      //TODO - implement searchText at this level
      if (this.searchText) {
        return this.inputs.filter((input) =>
          this.isStringOfCharsContainsSubstring(input.label, this.searchText)
        );
      }
      return this.inputs;
    },
    isInputsNotEmpty() {
      return !!this.filteredInputs.length;
    },
  },
  methods: {
    toggleDropdown(trueOrFalse) {
      this.showDropdown = trueOrFalse;
    },
    isStringOfCharsContainsSubstring(stringOfChars, substring) {
      return stringOfChars.toUpperCase().includes(substring?.toUpperCase());
    },
    updateAnnotations($event) {
      this.toggleDropdown(false);
      this.$emit("on-update-annotations", $event);
    },
    resetSearchText() {
      this.searchText = null;
    },
  },
};
</script>

<style lang="scss" scoped>
.dropdown {
  cursor: pointer;
  :deep(.dropdown__header) {
    max-height: 33px;
    font-weight: 500;
    min-width: 170px;
    @include font-size(13px);
    border: 1px solid palette(blue, 500);
    color: palette(blue, 500);
    &:after {
      border-color: palette(blue, 500);
    }
  }
}
</style>
