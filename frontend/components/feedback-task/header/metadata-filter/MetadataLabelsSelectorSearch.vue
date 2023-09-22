<template>
  <div class="search-area">
    <span v-if="selectedOptions.length" class="search-area__badges">
      <FilterBadge
        class="search-area__badge"
        v-for="option in selectedOptions"
        :key="option.label"
        :text="option.label"
        @on-clear="removeSelectedOption(option)"
      ></FilterBadge>
    </span>
    <input
      ref="search"
      id="searchLabel"
      class="search-area__input"
      type="text"
      autocomplete="off"
      :value="value"
      :placeholder="placeholder"
      @input="onInput($event)"
    />
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      default: "",
    },
    placeholder: {
      type: String,
      default: "",
    },
    selectedOptions: {
      type: Array,
    },
  },
  watch: {
    selectedOptions() {
      this.$refs.search.focus();
    },
  },
  mounted() {
    this.$refs.search.focus();
  },
  methods: {
    resetValue() {
      this.value.length && this.$emit("input", "");
    },
    onInput($event) {
      this.$emit("input", $event.target.value);
    },
    removeSelectedOption(option) {
      option.selected = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.search-area {
  display: flex;
  flex-direction: column;
  padding: 0 $base-space;
  border: 1px solid $black-10;
  border-radius: $border-radius-m;
  background: palette(white);
  overflow: hidden;
  transition: all 0.2s ease-out;
  &:focus-within {
    border-color: $primary-color;
    box-shadow: $shadow-300;
  }
  &:hover {
    transition: all 0.2s ease-in;
  }
  &__badges {
    display: flex;
    gap: calc($base-space / 2);
    flex-wrap: wrap;
    padding-top: $base-space;
  }
  &__input {
    height: 26px;
    width: 100%;
    border: none;
    @include font-size(13px);
    &:focus-visible {
      outline: 0;
    }
    @include input-placeholder {
      color: $black-37;
    }
  }
}
</style>
