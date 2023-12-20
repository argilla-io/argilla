<template>
  <div class="search-area">
    <span v-if="selectedOptions.length" class="search-area__badges">
      <FilterBadge
        class="search-area__badge"
        v-for="option in selectedOptions"
        :key="option.value"
        :text="option.text ?? option.value"
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
      :placeholder="selectedOptions.length ? '' : placeholder"
      @input="onInput($event)"
      @keydown.arrow-up.stop=""
      @keydown.arrow-down.stop=""
      @keydown.arrow-right.stop=""
      @keydown.arrow-left.stop=""
      @keydown.delete.exact.stop=""
      @keydown.enter.exact.stop=""
      @keydown.backspace.exact.stop=""
    />
    <BaseButton
      v-if="selectedOptions.length"
      class="search-area__close-button"
      @click="removeAll"
      title="Clear all"
    >
      <svgicon
        class="search-area__close-button__icon"
        name="close"
        width="10"
        height="10"
    /></BaseButton>
  </div>
</template>

<script>
import "assets/icons/close";
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
      this.$nextTick(() => {
        this.$refs.search.focus();
      });
    },
  },
  mounted() {
    this.$refs.search.focus();
  },
  methods: {
    onInput($event) {
      this.$emit("input", $event.target.value);
    },
    removeAll() {
      this.selectedOptions.forEach((opt) => {
        this.removeSelectedOption(opt);
      });
    },
    removeSelectedOption(option) {
      option.selected = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.search-area {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 0 $base-space;
  border: 1px solid $black-10;
  border-radius: $border-radius;
  background: palette(white);
  overflow: hidden;
  transition: all 0.2s ease-out;
  &:focus-within {
    border-color: $primary-color;
  }
  &:hover {
    transition: all 0.2s ease-in;
  }
  &__badges {
    display: flex;
    gap: calc($base-space / 2);
    flex-wrap: wrap;
    padding-top: $base-space;
    & ~ .search-area__input {
      min-height: 30px;
    }
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
  &__close-button {
    position: absolute;
    top: $base-space;
    right: $base-space;
    padding: calc($base-space / 2);
    background: $black-37;
    border-radius: $border-radius-rounded;
    &:hover {
      background: $black-54;
    }
    &__icon {
      color: palette(white);
    }
  }
}
</style>
