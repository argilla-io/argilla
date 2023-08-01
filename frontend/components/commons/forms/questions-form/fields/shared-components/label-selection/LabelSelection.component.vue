<template>
  <div class="container">
    <div class="component-header" v-if="showSearch || showCollapseButton">
      <div class="left-header">
        <SearchLabelComponent
          ref="searchComponentRef"
          v-if="showSearch"
          v-model="searchInput"
          :searchRef="searchRef"
          :placeholder="placeholder"
        />
      </div>
      <div class="right-header">
        <button
          ref="showLessButtonRef"
          type="button"
          class="show-less-button cursor-pointer"
          v-if="showCollapseButton"
          @click="toggleShowLess"
        >
          <span
            :class="isExpanded ? '--less' : '--more'"
            v-text="textToShowInTheCollapseButton"
          />
          <svgicon
            width="18"
            height="18"
            :name="iconToShowInTheCollapseButton"
          />
        </button>
      </div>
    </div>
    <transition-group
      ref="inputsAreaRef"
      :key="searchInput"
      name="shuffle"
      class="inputs-area"
      v-if="filteredOptions.length"
    >
      <div
        class="input-button"
        v-for="option in visibleOptions"
        :key="option.id"
      >
        <input
          type="checkbox"
          :name="option.text"
          :id="option.id"
          v-model="option.isSelected"
          @change="onSelect(option)"
        />
        <label
          class="label-text cursor-pointer"
          :class="{
            'label-active': option.isSelected,
            square: multiple,
            round: !multiple,
          }"
          :for="option.id"
          v-text="option.text"
          :title="option.text"
        />
      </div>
    </transition-group>
    <i class="no-result" v-if="!filteredOptions.length" />
  </div>
</template>

<script>
// NOTE - this threshold is used to show the search filter component for component from questionForm component
const OPTIONS_THRESHOLD_TO_ENABLE_SEARCH = 3;

export default {
  name: "LabelSelectionComponent",
  props: {
    maxOptionsToShowBeforeCollapse: {
      type: Number,
      default: () => -1,
    },
    options: {
      type: Array,
      required: true,
    },
    placeholder: {
      type: String,
      default: () => "Search labels",
    },
    componentId: {
      type: String,
      required: true,
    },
    multiple: {
      type: Boolean,
      default: () => false,
    },
  },
  model: {
    prop: "options",
    event: "on-change",
  },
  data() {
    return {
      searchInput: "",
      isExpanded: false,
    };
  },
  created() {
    this.searchRef = `${this.componentId}SearchFilterRef`;
  },
  computed: {
    filteredOptions() {
      return this.options.filter((option) =>
        String(option.text)
          .toLowerCase()
          .includes(this.searchInput.toLowerCase())
      );
    },
    remainingVisibleOptions() {
      return this.filteredOptions
        .slice(this.maxOptionsToShowBeforeCollapse)
        .filter((option) => option.isSelected);
    },
    visibleOptions() {
      if (this.maxOptionsToShowBeforeCollapse === -1 || this.isExpanded)
        return this.filteredOptions;

      return this.filteredOptions
        .slice(0, this.maxOptionsToShowBeforeCollapse)
        .concat(this.remainingVisibleOptions);
    },
    noResultMessage() {
      return `There is no result matching: ${this.searchInput}`;
    },
    numberToShowInTheCollapseButton() {
      return this.filteredOptions.length - this.visibleOptions.length;
    },
    showCollapseButton() {
      if (this.maxOptionsToShowBeforeCollapse === -1) return false;
      return this.filteredOptions.length > this.maxOptionsToShowBeforeCollapse;
    },
    showSearch() {
      return (
        this.options.length >= OPTIONS_THRESHOLD_TO_ENABLE_SEARCH ||
        this.showCollapseButton
      );
    },
    textToShowInTheCollapseButton() {
      if (this.isExpanded) {
        return "Less";
      }
      return `+${this.numberToShowInTheCollapseButton}`;
    },
    iconToShowInTheCollapseButton() {
      return this.isExpanded ? "chevron-up" : "chevron-down";
    },
  },
  methods: {
    onSelect({ id, isSelected }) {
      if (this.multiple) return;
      else {
        this.options.forEach((option) => {
          if (option.id === id) {
            option.isSelected = isSelected;
          } else {
            option.isSelected = false;
          }
          return option;
        });
      }
    },
    toggleShowLess() {
      this.isExpanded = !this.isExpanded;
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: $base-space * 2;
  .component-header {
    display: grid;
    grid-template-columns: 1fr auto;
    align-items: center;
  }
  .inputs-area {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: $base-space;
    border-radius: 5em;
    background: transparent;
    &:hover {
      border-color: darken(palette(purple, 800), 12%);
    }
  }
}

.show-less-button {
  display: flex;
  align-items: center;
  gap: $base-space;
  background: none;
  border: none;
  color: $black-37;
  font-weight: 500;
  text-decoration: none;
  .--more {
    border-radius: 20px;
    border: 1px solid $black-10;
    padding: 2px 4px;
    color: $black-54;
    @include font-size(12px);
  }
  .--less {
    @include font-size(14px);
  }
  .svg-icon {
    color: $black-37;
    border-radius: $border-radius;
  }
}

.label-text {
  display: block;
  width: 100%;
  height: 32px;
  min-width: 50px;
  max-width: 200px;
  text-align: center;
  padding-inline: 12px;
  background: palette(purple, 800);
  color: palette(purple, 200);
  line-height: 32px;
  font-weight: 500;
  outline: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border-radius: $border-radius-rounded;
  &:not(.label-active):hover {
    background: darken(palette(purple, 800), 8%);
  }
}

.round {
  border-radius: $border-radius-rounded;
}
.square {
  border-radius: $border-radius-s;
}

input[type="checkbox"] {
  display: none;
}
.label-active {
  color: white;
  background: #4c4ea3;
}
.no-result {
  display: block;
  height: $base-space * 4;
}
.cursor-pointer {
  cursor: pointer;
}

.shuffle-move {
  transition: transform 0.5s;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}
</style>
