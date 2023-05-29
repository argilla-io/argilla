<template>
  <div class="container">
    <div class="component-header">
      <input
        type="text"
        v-if="isSearch"
        :ref="searchRef"
        v-model.trim="searchInput"
        @keydown.shift.backspace.exact="looseFocus"
        @keydown.shift.space.exact="looseFocus"
        @keydown.arrow-right.stop=""
        @keydown.arrow-left.stop=""
        @keydown.delete.exact.stop=""
        @keydown.enter.exact.stop=""
      />

      <button
        type="button"
        v-if="isButtonShowMore"
        v-text="textToShowInTheButton"
        @click="toggleShowMore"
      />
    </div>
    <div class="inputs-area">
      <div
        class="input-button"
        v-for="option in filteredOptions"
        :key="option.id"
      >
        <input
          type="checkbox"
          :name="option.text"
          :id="option.id"
          v-model="option.value"
          @change="onSelect(option)"
        />
        <label
          class="label-text cursor-pointer"
          :class="{ 'label-active': option.value }"
          :for="option.id"
          v-text="option.text"
        />
      </div>

      <i
        class="no-result"
        v-if="!filteredOptions.length"
        v-text="noResultMessage"
      />
    </div>
  </div>
</template>

<script>
const MAX_OPTION_TO_SHOW = 30;
// const MAX_OPTION_TO_SHOW = 2;

export default {
  name: "SingleLabelMonoSelectionComponent",
  props: {
    options: {
      type: Array,
      required: true,
    },
    componentId: {
      type: String,
      required: true,
    },
    isSearch: {
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
      showMore: false,
    };
  },
  created() {
    this.searchRef = `${this.componentId}SearchFilterRef`;
  },
  computed: {
    filteredOptions() {
      return this.options
        .filter((option) => String(option.text).includes(this.searchInput))
        .slice(0, this.showMore ? this.options.length : MAX_OPTION_TO_SHOW);
    },
    noResultMessage() {
      return `There is no result matching: ${this.searchInput}`;
    },
    numberToShowInTheButton() {
      if (!this.searchInput.length) {
        return this.options.length - this.filteredOptions.length;
      }
      if (this.filteredOptions.length > MAX_OPTION_TO_SHOW) {
        return this.filteredOptions.length - MAX_OPTION_TO_SHOW;
      }
      return 0;
    },
    isButtonShowMore() {
      return this.numberToShowInTheButton;
    },
    textToShowInTheButton() {
      if (this.showMore) {
        return "Show less";
      }
      return `+${this.numberToShowInTheButton}`;
    },
  },
  methods: {
    onSelect({ id, value }) {
      this.options.map((option) => {
        if (option.id === id) {
          option.value = value;
        } else {
          option.value = false;
        }
        return option;
      });

      this.$emit("on-change", this.options);
    },
    looseFocus() {
      this.$refs[this.searchRef].blur();
    },
    toggleShowMore() {
      this.showMore = !this.showMore;
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  .component-header {
    display: flex;
    justify-content: space-between;
  }
  .inputs-area {
    display: inline-flex;
    gap: $base-space;
    border-radius: 5em;
    background: transparent;
    &:hover {
      border-color: darken(palette(purple, 800), 12%);
    }
  }
}
.label-text {
  display: flex;
  width: 100%;
  border-radius: 2px;
  height: 40px;
  background: palette(purple, 800);
  outline: none;
  padding-left: 16px;
  padding-right: 16px;
  line-height: 40px;
  font-weight: 500;
  overflow: hidden;
  color: palette(purple, 200);
  box-shadow: 0;
  transition: all 0.2s ease-in-out;
  &:not(.label-active):hover {
    background: darken(palette(purple, 800), 8%);
  }
}
input[type="checkbox"] {
  display: none;
}
.label-active {
  color: white;
  background: #4c4ea3;
}
.cursor-pointer {
  cursor: pointer;
}
</style>
