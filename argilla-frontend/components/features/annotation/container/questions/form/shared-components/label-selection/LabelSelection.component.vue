<template>
  <div class="container" @keydown="keyboardHandler">
    <div class="component-header" v-if="showSearch || showCollapseButton">
      <div class="left-header">
        <SearchLabelComponent
          v-if="showSearch"
          ref="searchComponentRef"
          v-model="searchInput"
          :searchRef="searchRef"
          :placeholder="$t('spanAnnotation.searchLabels')"
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
      :css="options.length < 50"
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
          :data-keyboard="keyboards[option.id]"
          v-model="option.isSelected"
          @change="onSelect(option)"
          @focus="onFocus"
          @keydown.tab="expandLabelsOnTab(index)"
        />
        <BaseTooltip
          :title="isSuggested(option) ? $t('suggestion.name') : ''"
          :text="getSuggestedAgent(option)"
          minimalist
        >
          <label
            class="label-text"
            :class="{
              'label-active': option.isSelected,
              square: multiple,
              round: !multiple,
            }"
            :for="option.id"
            :title="option.text"
          >
            <span class="key" v-text="keyboards[option.id]" />
            <span class="label-text__text">{{ option.text }}</span>
            <span v-if="isSuggested(option)" class="label-text__suggestion">
              <svgicon class="label-text__suggestion__icon" name="suggestion" />
              <span
                v-if="getSuggestedScore(option)"
                class="label-text__suggestion__score"
                v-text="getSuggestedScore(option)"
              />
            </span>
          </label>
        </BaseTooltip>
      </div>
    </transition-group>
    <i class="no-result" v-if="!filteredOptions.length" />
  </div>
</template>

<script>
const OPTIONS_THRESHOLD_TO_ENABLE_SEARCH = 15;
import "assets/icons/chevron-down";
import "assets/icons/chevron-up";

import { useLabelSelectionViewModel } from "./useLabelSelectionViewModel";

export default {
  name: "LabelSelectionComponent",
  props: {
    maxOptionsToShowBeforeCollapse: {
      type: Number,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
    suggestion: {
      type: Object,
    },
    componentId: {
      type: String,
      required: true,
    },
    multiple: {
      type: Boolean,
      default: () => false,
    },
    suggestionFirst: {
      type: Boolean,
      default: () => false,
    },
    isFocused: {
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
    keyboards() {
      return this.options.reduce((acc, option, index) => {
        acc[option.id] = index + 1;
        return acc;
      }, {});
    },
    filteredOptions() {
      return this.options.filter((option) =>
        String(option.text)
          .toLowerCase()
          .includes(this.searchInput.toLowerCase())
      );
    },
    visibleOptions() {
      let options = this.filteredOptions;

      if (this.suggestionFirst) {
        const suggestedOptions = this.filteredOptions
          .filter(
            (v) => this.suggestion && this.suggestion.isSuggested(v.value)
          )
          .sort((a, b) => {
            const isASuggested = this.suggestion.getSuggestion(a.value);
            const isBSuggested = this.suggestion.getSuggestion(b.value);

            return isASuggested?.score > isBSuggested?.score ? -1 : 1;
          });

        const noSuggestedOptions = this.filteredOptions.filter(
          (v) => !this.suggestion || !this.suggestion.isSuggested(v.value)
        );

        options = [...suggestedOptions, ...noSuggestedOptions];
      }

      if (this.isExpanded) {
        return options;
      }

      const remainingSorted = options
        .slice(this.maxOptionsToShowBeforeCollapse)
        .filter((option) => option.isSelected);

      return options
        .slice(0, this.maxOptionsToShowBeforeCollapse)
        .concat(remainingSorted);
    },
    numberToShowInTheCollapseButton() {
      return this.filteredOptions.length - this.visibleOptions.length;
    },
    showCollapseButton() {
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
        $event.key === "ArrowLeft" ||
        $event.key === "ArrowRight" ||
        $event.key === "ArrowUp" ||
        $event.key === "ArrowDown" ||
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
        $event.stopPropagation();

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
      if (!this.showCollapseButton) return;

      if (index === this.maxOptionsToShowBeforeCollapse - 1) {
        this.isExpanded = true;
      }
    },
    isSuggested(option) {
      return this.suggestion?.isSuggested(option.value);
    },
    getSuggestedScore(option) {
      return this.suggestion?.getSuggestion(option.value)?.score?.fixed;
    },
    getSuggestedAgent(option) {
      return this.suggestion?.getSuggestion(option.value)?.agent;
    },
  },
  setup(props) {
    return useLabelSelectionViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: $base-space * 2;
  .component-header {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    height: 28px;
  }
  .inputs-area {
    display: inline-flex;
    align-items: center;
    flex-wrap: wrap;
    gap: $base-space;
    border-radius: 5em;
    background: transparent;
    &:hover {
      border-color: hsl(from var(--bg-label) h s l / 80%);
    }
  }

  .input-button {
    max-width: 100%;
  }
}

.show-less-button {
  display: flex;
  align-items: center;
  gap: $base-space;
  background: none;
  border: none;
  color: var(--fg-tertiary);
  font-weight: 500;
  text-decoration: none;
  .--more {
    border-radius: 20px;
    border: 1px solid var(--bg-opacity-10);
    padding: 2px 4px;
    color: var(--fg-secondary);
    @include font-size(12px);
  }
  .--less {
    @include font-size(14px);
  }
  .svg-icon {
    color: var(--fg-tertiary);
    border-radius: $border-radius;
  }
}

.label-text {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: $base-space;
  width: 100%;
  min-height: $base-space * 4;
  min-width: 50px;
  text-align: center;
  padding-inline: $base-space;
  background: var(--bg-label-unselected);
  color: var(--fg-label);
  font-weight: 500;
  outline: none;
  border: 2px solid transparent;
  border-radius: $border-radius-rounded;
  transition: all 0.2s ease-in-out;
  cursor: pointer;
  user-select: none;
  &__text {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    min-width: 0;
  }
  &__suggestion {
    display: flex;
    flex-shrink: 0;
    align-items: center;
    gap: calc($base-space / 2);
    &__score {
      @include font-size(11px);
    }
    &__icon {
      flex-shrink: 0;
      width: 10px;
      height: 10px;
    }
  }

  &:not(.label-active):hover {
    background: var(--bg-label-unselected-hover);
    transition: all 0.2s ease-in-out;
  }

  &.label-active {
    color: white;
    background: var(--bg-label);
    box-shadow: none;
    &:hover {
      box-shadow: inset 0 -2px 6px 0 hsl(from var(--bg-label) h s l / 80%);
      background: hsl(from var(--bg-label) h s l / 80%);
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
    & + div .label-text {
      outline: 2px solid var(--fg-cuaternary);
    }
  }
}
.input-button:not(:first-of-type) {
  input[type="checkbox"] {
    &:focus:not(:focus-visible) {
      & + div .label-text {
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
  min-width: 12px;
  padding: 2px;
  line-height: 1;
  border-radius: $border-radius;
  border-width: 1px 1px 3px 1px;
  border-color: var(--fg-shortcut-key);
  border-style: solid;
  box-sizing: content-box;
  color: var(--fg-primary);
  background: var(--bg-solid-grey-2);
  @include font-size(11px);
  font-family: monospace, monospace;
}
.no-result {
  display: block;
  height: $base-space * 4;
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
