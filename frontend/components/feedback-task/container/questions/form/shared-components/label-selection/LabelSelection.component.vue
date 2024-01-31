<template>
  <div class="container" @keydown="keyboardHandler">
    <div class="component-header" v-if="showSearch || showCollapseButton">
      <div class="left-header">
        <SearchLabelComponent
          v-if="showSearch"
          ref="searchComponentRef"
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
        v-for="(option, index) in visibleOptions"
        :key="option.id"
        @keydown.enter.prevent
      >
        <input
          ref="options"
          type="checkbox"
          :name="option.text"
          :id="option.id"
          :data-keyboard="option.keyboard"
          v-model="option.isSelected"
          @change="onSelect(option)"
          @focus="onFocus"
          @keydown.tab="expandLabelsOnTab(index)"
        />
        <label
          class="label-text"
          :class="{
            'label-active': option.isSelected,
            '--suggestion': hasSuggestion(option.text),
            square: multiple,
            round: !multiple,
          }"
          :for="option.id"
          :data-title="
            hasSuggestion(option.text)
              ? `${$t('suggestion.name')}: ${option.text}`
              : option.isSelected
              ? $t('annotation')
              : null
          "
          :title="option.text"
        >
          <span
            class="key"
            v-if="showShortcutsHelper"
            v-text="option.keyboard"
          />
          <span>{{ option.text }}</span>
        </label>
      </div>
    </transition-group>
    <i class="no-result" v-if="!filteredOptions.length" />
  </div>
</template>

<script>
const OPTIONS_THRESHOLD_TO_ENABLE_SEARCH = 3;

import "assets/icons/chevron-down";
import "assets/icons/chevron-up";
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
    suggestions: {
      type: [Array, String],
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
    isFocused: {
      type: Boolean,
      default: () => false,
    },
    showShortcutsHelper: {
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
      timer: null,
      keyCode: "",
    };
  },
  created() {
    this.searchRef = `${this.componentId}SearchFilterRef`;
  },
  watch: {
    isFocused: {
      immediate: true,
      handler(newValue) {
        if (newValue) {
          this.$nextTick(() => {
            const options = this.$refs?.options;
            if (options.some((o) => o.contains(document.activeElement))) {
              return;
            }

            if (options.length > 0) {
              options[0].focus({
                preventScroll: true,
              });
            } else {
              this.$refs.searchComponentRef?.searchInputRef.focus();
            }
          });
        }
      },
    },
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
        return this.$t("less");
      }

      return `+${this.numberToShowInTheCollapseButton}`;
    },
    iconToShowInTheCollapseButton() {
      return this.isExpanded ? "chevron-up" : "chevron-down";
    },
  },
  methods: {
    keyboardHandler($event) {
      if (this.timer) clearTimeout(this.timer);

      if (
        $event.key === "Tab" ||
        $event.key === "Enter" ||
        $event.key === "Backspace" ||
        $event.shiftKey ||
        $event.ctrlKey ||
        $event.metaKey
      )
        return;

      const isSearchActive =
        document.activeElement ===
        this.$refs.searchComponentRef?.searchInputRef;

      if (isSearchActive) return;

      if ($event.code == "Space") {
        $event.preventDefault();
        document.activeElement.click();

        return;
      }

      this.keyCode += $event.key;

      if (isNaN(this.keyCode)) {
        this.$refs.searchComponentRef?.focusInSearch();

        return this.reset();
      }

      if (this.hasJustOneCoincidence(this.keyCode)) {
        return this.selectByKeyCode($event, this.keyCode);
      }

      this.timer = setTimeout(() => {
        this.selectByKeyCode($event, this.keyCode);
      }, 300);
    },
    hasJustOneCoincidence(keyCode) {
      return (
        this.$refs.options.filter((o) => o.dataset.keyboard.startsWith(keyCode))
          .length == 1
      );
    },
    reset() {
      this.keyCode = "";
      this.timer = null;
    },
    selectByKeyCode($event, keyCode) {
      const match = this.$refs.options.find(
        (option) => option.dataset.keyboard === keyCode
      );

      if (match) {
        $event.preventDefault();

        match.click();
      }

      this.reset();
    },
    onSelect({ id, isSelected }) {
      if (this.multiple) return;

      this.options.forEach((option) => {
        option.isSelected = option.id === id ? isSelected : false;
      });

      if (isSelected) {
        this.$emit("on-selected");
      }
    },
    toggleShowLess() {
      this.isExpanded = !this.isExpanded;
    },
    onFocus() {
      this.$emit("on-focus");
    },
    expandLabelsOnTab(index) {
      if (!this.showCollapseButton) {
        return;
      }
      if (index === this.maxOptionsToShowBeforeCollapse - 1) {
        this.isExpanded = true;
      }
    },
    hasSuggestion(value) {
      return this.suggestions?.includes(value) || false;
    },
  },
  beforeMount() {
    this.options.forEach((option, index) => {
      option.keyboard = index + 1;
    });
  },
};
</script>

<style lang="scss" scoped>
$suggestion-color: palette(yellow, 400);
$label-color: palette(purple, 800);
$label-dark-color: palette(purple, 200);
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
      border-color: darken($label-color, 12%);
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
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $base-space;
  width: 100%;
  height: 32px;
  min-width: 50px;
  max-width: 200px;
  text-align: center;
  padding-inline: $base-space;
  background: $label-color;
  color: $label-dark-color;
  font-weight: 500;
  outline: none;
  border: 2px solid transparent;
  border-radius: $border-radius-rounded;
  cursor: pointer;
  span {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    min-width: 0;
  }
  &.--suggestion {
    background: $suggestion-color;
    &:not(.label-active):hover {
      background: darken($suggestion-color, 8%);
    }
  }
  &:not(.label-active):hover {
    background: darken($label-color, 8%);
  }
  &.label-active {
    color: white;
    background: $label-dark-color;
    &.--suggestion {
      border: 2px solid $suggestion-color;
    }
  }
}

.round {
  border-radius: $border-radius-rounded;
}
.square {
  border-radius: $border-radius-s;
}

input[type="checkbox"] {
  @extend %visuallyhidden;
  &:focus {
    & + .label-text {
      outline: 2px solid $primary-color;
    }
  }
}
.input-button:not(:first-of-type) {
  input[type="checkbox"] {
    &:focus:not(:focus-visible) {
      & + .label-text {
        outline: none;
        &.label-active {
          outline: none;
        }
      }
    }
  }
}
.key {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  height: $base-space * 2;
  aspect-ratio: 1;
  border-radius: $border-radius;
  border-width: 1px 1px 3px 1px;
  border-color: $black-20;
  border-style: solid;
  box-sizing: content-box;
  color: $black-87;
  background: palette(grey, 700);
  @include font-size(11px);
  font-family: monospace, monospace;
}
.no-result {
  display: block;
  height: $base-space * 4;
}

[data-title] {
  position: relative;
  overflow: visible;
  @include tooltip-mini("top");
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
