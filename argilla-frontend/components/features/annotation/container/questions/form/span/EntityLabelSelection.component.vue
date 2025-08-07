<template>
  <div
    class="container"
    v-click-outside="clickOutside"
    @keydown="keyboardHandler"
  >
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
            aria-hidden="true"
          />
        </button>
      </div>
    </div>
    <transition-group
      ref="inputsAreaRef"
      :key="searchInput"
      :css="options.length < 50"
      name="shuffle"
      class="inputs-area"
      v-if="filteredOptions.length"
      role="listbox"
      :aria-multiselectable="true"
      aria-label="Label-Options"
    >
      <EntityLabelBadge
        v-for="(option, index) in visibleOptions"
        :key="option.id"
        ref="options"
        :visible-shortcuts="visibleShortcuts"
        :option="option"
        :keyboards="keyboards"
        v-model="option.isSelected"
        @keydown.enter.prevent
        @on-selected="onSelect(option)"
        @on-expand-labels-on-tab="expandLabelsOnTab(index)"
        @on-focus="onFocus"
        role="option"
      />
    </transition-group>
    <i class="no-result" v-if="!filteredOptions.length" />
  </div>
</template>

<script>
const OPTIONS_THRESHOLD_TO_ENABLE_SEARCH = 15;
import "assets/icons/chevron-down";
import "assets/icons/chevron-up";
export default {
  name: "EntityLabelSelectionComponent",
  props: {
    maxOptionsToShowBeforeCollapse: {
      type: Number,
    },
    options: {
      type: Array,
      required: true,
    },
    componentId: {
      type: String,
      required: true,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
    enableSpanQuestionShortcutsGlobal: {
      type: Boolean,
      default: () => false,
    },
    visibleShortcuts: {
      type: Boolean,
      default: true,
    },
  },
  model: {
    prop: "options",
    event: "on-change",
  },
  data() {
    return {
      isOutside: false,
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
        this.isOutside = !newValue;
        if (newValue) {
          this.$nextTick(() => {
            const options = this.$refs?.options;

            if (
              options.some((o) =>
                o.$refs.inputRef.contains(document.activeElement)
              )
            ) {
              return;
            }

            if (options.length > 0) {
              options[0].$refs.inputRef.focus({
                preventScroll: true,
              });
            } else {
              this.$refs.searchComponentRef?.searchInputRef.focus();
            }
          });
        }
      },
    },
    isOutside() {
      if (!this.enableSpanQuestionShortcutsGlobal) return;
      if (this.isOutside) {
        document.addEventListener("keydown", this.keyboardHandler);
      } else {
        document.removeEventListener("keydown", this.keyboardHandler);
      }
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
    remainingVisibleOptions() {
      return this.filteredOptions
        .slice(this.maxVisibleOptions)
        .filter((option) => option.isSelected);
    },
    visibleOptions() {
      if (this.isExpanded) return this.filteredOptions;

      return this.filteredOptions
        .slice(0, this.maxVisibleOptions)
        .concat(this.remainingVisibleOptions);
    },
    maxVisibleOptions() {
      return this.maxOptionsToShowBeforeCollapse ?? this.options.length + 1;
    },
    numberToShowInTheCollapseButton() {
      return this.filteredOptions.length - this.visibleOptions.length;
    },
    showCollapseButton() {
      return this.filteredOptions.length > this.maxVisibleOptions;
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
    clickOutside() {
      this.isOutside = true;
    },
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
        this.$refs.options.filter((o) =>
          o.$refs.inputRef.dataset.keyboard.startsWith(keyCode)
        ).length == 1
      );
    },
    reset() {
      this.keyCode = "";
      this.timer = null;
    },
    selectByKeyCode($event, keyCode) {
      const match = this.$refs.options.find(
        (option) => option.$refs.inputRef.dataset.keyboard === keyCode
      )?.$refs.inputRef;

      if (match) {
        $event.preventDefault();
        $event.stopPropagation();

        match.click();
      }

      this.reset();
    },
    onSelect({ id, isSelected }) {
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

      if (index === this.maxVisibleOptions - 1) {
        this.isExpanded = true;
      }
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
