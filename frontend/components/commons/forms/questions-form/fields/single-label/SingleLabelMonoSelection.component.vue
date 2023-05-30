<template>
  <div class="container">
    <div class="component-header" v-if="isSearch || isButtonShowMore">
      <div class="left-header">
        <SearchSingleLabelComponent
          v-if="isSearch"
          v-model="searchInput"
          :searchRef="searchRef"
          :placeholder="placeholder"
        />
      </div>

      <div class="right-header">
        <button
          type="button"
          class="show-more-button cursor-pointer"
          v-if="isButtonShowMore"
          v-text="textToShowInTheButton"
          @click="toggleShowMore"
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
    </transition-group>
    <i
      class="no-result"
      v-if="!filteredOptions.length"
      v-text="noResultMessage"
    />
  </div>
</template>

<script>
const MAX_OPTION_TO_SHOW = 30;

export default {
  name: "SingleLabelMonoSelectionComponent",
  props: {
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
      return null;
    },
    isButtonShowMore() {
      return this.numberToShowInTheButton || this.showMore;
    },
    textToShowInTheButton() {
      if (this.showMore) {
        return "Show less";
      }
      return `+${this.numberToShowInTheButton}`;
    },
  },
  watch: {
    searchInput() {
      this.resetShowMore();
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
    resetShowMore() {
      this.showMore = false;
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
  gap: $base-space * 2;
  .component-header {
    display: grid;
    grid-template-columns: 1fr auto;
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

.show-more-button {
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
