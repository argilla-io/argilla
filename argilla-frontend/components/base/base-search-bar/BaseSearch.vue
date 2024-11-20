<template>
  <div class="search-area">
    <input
      ref="search"
      id="searchLabel"
      class="search-area__input"
      type="text"
      autocomplete="off"
      :value="value"
      :placeholder="placeholder"
      @input="onInput($event)"
      @keydown.stop=""
    />
    <BaseButton
      v-if="value.length"
      class="search-area__close-button"
      @click="removeSearch"
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
  },
  mounted() {
    this.$nextTick(() => {
      this.$refs.search.focus();
    });
  },
  methods: {
    onInput($event) {
      this.$emit("input", $event.target.value);
    },
    removeSearch() {
      this.$emit("input", "");
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
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius;
  overflow: hidden;
  transition: all 0.2s ease-out;
  &:focus-within {
    border-color: var(--fg-cuaternary);
  }
  &:hover {
    transition: all 0.2s ease-in;
  }
  &__input {
    height: 26px;
    width: 100%;
    border: none;
    background: transparent;
    @include font-size(13px);
    color: var(--fg-primary);
    &:focus-visible {
      outline: 0;
    }
    @include input-placeholder {
      color: var(--fg-tertiary);
    }
  }
  &__close-button {
    position: absolute;
    right: 0;
    padding: $base-space;
    &__icon {
      color: var(--fg-secondary);
    }
  }
}
</style>
