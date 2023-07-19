<template>
  <div class="search-area" @click="focusInSearch">
    <BaseIconWithBadge
      ref="iconSearchRef"
      class="search-area__icon --search"
      icon="search"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      tabindex="-1"
      aria-hidden="true"
    />
    <input
      class="search-input"
      type="text"
      :value="value"
      :ref="searchRef"
      :placeholder="placeholder"
      @input="$emit('input', $event.target.value)"
      @keydown.shift.backspace.exact="looseFocus"
      @keydown.shift.space.exact="looseFocus"
      @keydown.arrow-right.stop=""
      @keydown.arrow-left.stop=""
      @keydown.delete.exact.stop=""
      @keydown.enter.exact.stop=""
    />
    <BaseIconWithBadge
      v-if="value"
      ref="iconCloseRef"
      class="search-area__icon --close"
      icon="close"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      @click-icon="resetValue"
    />
  </div>
</template>

<script>
export default {
  name: "SearchLabelComponent",
  props: {
    value: {
      type: String,
      default: () => "",
    },
    searchRef: {
      type: String,
      required: true,
    },
    placeholder: {
      type: String,
      default: () => "",
    },
  },
  computed: {
    searchInputRef() {
      return this.$refs[this.searchRef];
    },
  },
  methods: {
    looseFocus() {
      this.searchInputRef.blur();
    },
    focusInSearch() {
      this.searchInputRef.focus();
    },
    resetValue() {
      this.value.length && this.$emit("input", "");
    },
  },
};
</script>

<style lang="scss" scoped>
.search-area {
  display: flex;
  align-items: center;
  gap: calc($base-space / 2);
  width: 14.5em;
  padding: 0 $base-space;
  border: 1px solid $black-10;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: $shadow-300;
  transition: all 0.2s ease-out;
  &:focus-within {
    border-color: $primary-color;
    box-shadow: $shadow-300;
  }
  &:hover {
    box-shadow: $shadow-400;
    transition: all 0.2s ease-in;
  }
  &__icon {
    flex-shrink: 0;
    padding: 0;
    background: transparent;
    width: 18px;
    height: 18px;
    transition: none;
    &.--search {
      cursor: default;
    }
    &.--close {
      height: 12px;
      width: 12px;
    }
  }
}

.search-input {
  height: 28px;
  width: 100%;
  border: none;
  border-radius: 10px;
  line-height: 28px;
  &:focus-visible {
    outline: 0;
  }
  @include input-placeholder {
    color: $black-37;
  }
}
</style>
