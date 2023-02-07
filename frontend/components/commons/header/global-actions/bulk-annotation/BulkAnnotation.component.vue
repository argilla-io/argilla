<template>
  <filter-dropdown :visible="showDropdown" @visibility="toggleDropdown">
    <template #dropdown-header>
      <span data-title="Annotate">
        <svgicon name="pen" />
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
            :hasInputsChanged="hasAnnotationsChanged"
            @on-change="updateLastSelectedAnnotation"
            @on-submit="updateAnnotations"
            @on-reset="resetLastSelectedAnnotation"
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
import _ from "lodash";
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
      lastSelectedAnnotation: { ID: null, VALUE: null },
      clonedInputs: [],
    };
  },
  computed: {
    updatedAnnotations() {
      const updatedAnnotations = this.clonedInputs.map((input) => {
        if (input.id === this.lastSelectedAnnotation.ID) {
          input.selected = this.lastSelectedAnnotation.VALUE;
        }
        return input;
      });
      return updatedAnnotations;
    },
    filteredInputs() {
      if (this.searchText) {
        return this.updatedAnnotations.filter((input) =>
          this.isStringOfCharsContainsSubstring(input.label, this.searchText)
        );
      }
      return this.updatedAnnotations;
    },
    isInputsNotEmpty() {
      return !!this.filteredInputs.length;
    },
    hasAnnotationsChanged() {
      return _.isEqual(this.inputs, this.updatedAnnotations);
    },
  },
  updated() {
    this.resetLastSelectedAnnotation();
  },
  methods: {
    rerenderComponent() {
      return !!this.inputs;
    },
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
    resetLastSelectedAnnotation() {
      this.updateLastSelectedAnnotation({ ID: null, VALUE: null });
      this.clonedInputs = structuredClone(this.inputs);
    },
    updateLastSelectedAnnotation({ ID, VALUE }) {
      this.lastSelectedAnnotation = { ID, VALUE };
    },
    resetSearchText() {
      this.searchText = null;
    },
  },
};
</script>
