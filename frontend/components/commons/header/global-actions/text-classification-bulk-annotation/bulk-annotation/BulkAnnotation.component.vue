<template>
  <filter-dropdown :visible="showDropdown" @visibility="toggleDropdown">
    <template #dropdown-header>
      <span data-title="Annotate">
        <svgicon name="pen"></svgicon>
      </span>
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
import "assets/icons/pen";
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
</style>
