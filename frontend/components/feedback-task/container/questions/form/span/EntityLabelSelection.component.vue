<template>
  <div class="container">
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
      <EntityLabelBadge
        v-for="(option, index) in visibleOptions"
        :key="option.id"
        ref="options"
        :option="option"
        :showShortcutsHelper="showShortcutsHelper && enableShortcuts"
        :keyboards="keyboards"
        v-model="option.isSelected"
        @keydown.enter.prevent
        @on-selected="onSelect(option)"
        @on-expand-labels-on-tab="expandLabelsOnTab(index)"
        @on-focus="onFocus"
      />
    </transition-group>
    <i class="no-result" v-if="!filteredOptions.length" />
  </div>
</template>

<script>
const OPTIONS_THRESHOLD_TO_ENABLE_SEARCH = 3;
import "assets/icons/chevron-down";
import "assets/icons/chevron-up";
export default {
  name: "EntityLabelSelectionComponent",
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
    isFocused: {
      type: Boolean,
      default: () => false,
    },
    showShortcutsHelper: {
      type: Boolean,
      default: () => false,
    },
    enableShortcuts: {
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

            if (options.some((o) => o.$el.contains(document.activeElement))) {
              return;
            }

            if (options.length > 0) {
              options[0].$el.focus({
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

      if ($event.shiftKey || $event.ctrlKey || $event.metaKey) return;

      const isAnInput = document.activeElement.tagName === "INPUT";

      if (isAnInput) return;

      this.keyCode += $event.key;

      if (isNaN(this.keyCode)) {
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

        match.click();
      }

      this.reset();
    },
    onSelect({ id, isSelected }) {
      this.options.forEach((option) => {
        option.isSelected = option.id === id;
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
  },
  mounted() {
    if (this.enableShortcuts) {
      document.addEventListener("keydown", this.keyboardHandler);
    }
  },
  destroyed() {
    if (this.enableShortcuts) {
      document.removeEventListener("keydown", this.keyboardHandler);
    }
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
