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
            @on-remove="removeAnnotation"
            @on-submit="updateAnnotations"
            @on-reset="resetAll"
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
    recordsIds: {
      type: Set,
      required: true,
    },
  },
  data() {
    return {
      clonedInputs: [],
      showDropdown: false,
      searchText: null,
      lastSelectedAnnotation: {
        ID: null,
        VALUE: null,
        RECORD_IDS: null,
        REMOVED: null,
      },
    };
  },
  computed: {
    sortedInputsBySelectedRecords() {
      return this.inputs.sort((a, b) =>
        a.record_ids.size > b.record_ids.size ? -1 : 1
      );
    },
    updatedAnnotations() {
      const updatedAnnotations = this.clonedInputs.map((input) => {
        if (input.id === this.lastSelectedAnnotation.ID) {
          input.selected = this.lastSelectedAnnotation.VALUE;
          input.record_ids = this.lastSelectedAnnotation.RECORD_IDS;
          input.removed = this.lastSelectedAnnotation.REMOVED;
        }
        return input;
      });
      return updatedAnnotations;
    },
    filteredInputs() {
      if (this.searchText) {
        return this.updatedAnnotations.filter(({ label }) =>
          this.isStringOfCharsContainsSubstring(label, this.searchText)
        );
      }
      return this.updatedAnnotations;
    },
    isInputsNotEmpty() {
      return !!this.filteredInputs.length;
    },
    hasAnnotationsChanged() {
      return _.isEqual(
        this.sortedInputsBySelectedRecords,
        this.updatedAnnotations
      );
    },
  },
  updated() {
    this.resetAll();
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
    updateAnnotations(updatedAnnotations) {
      this.toggleDropdown(false);
      this.$emit("on-update-annotations", updatedAnnotations);
    },
    resetAll() {
      this.updateLastSelectedAnnotation({
        ID: null,
        VALUE: null,
        RECORD_IDS: null,
        REMOVED: false,
      });
      this.clonedInputs = structuredClone(this.sortedInputsBySelectedRecords);
    },
    updateLastSelectedAnnotation({ ID, VALUE, REMOVED }) {
      const initialInputObj = this.inputs.find((input) => input.id === ID);
      this.lastSelectedAnnotation = {
        ID,
        VALUE,
        RECORD_IDS:
          VALUE && initialInputObj?.record_ids
            ? this.recordsIds
            : initialInputObj?.record_ids,
        REMOVED: _.isNil(initialInputObj?.removed)
          ? REMOVED
          : initialInputObj.removed,
      };
    },
    removeAnnotation({ ID }) {
      this.lastSelectedAnnotation = {
        ID,
        VALUE: false,
        RECORD_IDS: [],
        REMOVED: true,
      };
    },
    resetSearchText() {
      this.searchText = null;
    },
  },
};
</script>
