<template>
  <div class="container">
    <div class="component-header" v-if="showSearch || showCollapseButton">
      <div class="left-header">
        <SearchSingleLabelComponent
          v-if="showSearch"
          v-model="searchInput"
          :searchRef="searchRef"
          :placeholder="placeholder"
        />
      </div>

      <div class="right-header">
        <button
          type="button"
          class="show-less-button cursor-pointer"
          v-if="showCollapseButton"
          v-text="textToShowInTheCollapseButton"
          @click="toggleShowLess"
        />
      </div>
    </div>
    <transition-group
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
          v-model="option.is_selected"
          @change="onSelect(option)"
        />
        <label
          class="label-text cursor-pointer"
          :class="{ 'label-active': option.is_selected }"
          :for="option.id"
          v-text="option.text"
        />
      </div>
    </transition-group>
    <i
      class="no-result"
      v-if="!filteredOptions.length"
      v-text="noResultMessage"
    />
  </div>
</template>

<script>
export default {
  name: "SingleLabelMonoSelectionComponent",
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
    showSearch: {
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
      showLess: false,
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
    visibleOptions() {
      if (!this.showCollapseButton || this.showLess)
        return this.filteredOptions;

      return this.filteredOptions.slice(
        0,
        this.maxOptionsToShowBeforeCollapse + 1
      );
    },
    noResultMessage() {
      return `There is no result matching: ${this.searchInput}`;
    },
    numberToShowInTheCollapseButton() {
      return this.filteredOptions.length - this.maxOptionsToShowBeforeCollapse;
    },
    showCollapseButton() {
      if (this.maxOptionsToShowBeforeCollapse === -1) return false;
      if (this.numberToShowInTheCollapseButton < 0) return false;
      return this.options.length > this.maxOptionsToShowBeforeCollapse;
    },
    textToShowInTheCollapseButton() {
      if (this.showLess) {
        return "Show less";
      }
      return `+${this.numberToShowInTheCollapseButton}`;
    },
  },
  methods: {
    onSelect({ id, is_selected }) {
      this.options.map((option) => {
        if (option.id === id) {
          option.is_selected = is_selected;
        } else {
          option.is_selected = false;
        }
        return option;
      });

      this.$emit("on-change", this.options);
    },
    toggleShowLess() {
      this.showLess = !this.showLess;
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
  }
  .inputs-area {
    display: inline-flex;
    gap: $base-space;
    flex-wrap: wrap;
    border-radius: 5em;
    background: transparent;
    &:hover {
      border-color: darken(palette(purple, 800), 12%);
    }
  }
}

.show-less-button {
  background: none;
  border: none;
  color: rgba(0, 0, 0, 0.6);
  text-decoration: none;
  &:hover {
    color: rgba(0, 0, 0, 0.87);
  }
}

.label-text {
  display: flex;
  width: 100%;
  border-radius: 50em;
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
