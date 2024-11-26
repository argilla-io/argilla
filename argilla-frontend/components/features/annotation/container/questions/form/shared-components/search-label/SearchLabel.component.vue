<template>
  <div class="search-area" @click="focusInSearch" aria-label="Search Labels">
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
      id="searchLabel"
      class="search-input"
      type="text"
      :value="value"
      :ref="searchRef"
      :placeholder="placeholder"
      role="search"
      @input="$emit('input', $event.target.value)"
      @keydown.arrow-up.prevent="looseFocus"
      @keydown.arrow-down.prevent="looseFocus"
      @keydown.stop=""
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
      aria-hidden="true"
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
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius-xl;
  overflow: hidden;
  transition: all 0.2s ease-out;
  &:focus-within {
    border-color: var(--bg-action);
  }
  &:hover {
    transition: all 0.2s ease-in;
  }
  &__icon {
    flex-shrink: 0;
    padding: 0;
    background: transparent;
    width: $base-space * 2;
    height: $base-space * 2;
    transition: none;
    &.--search {
      cursor: default;
    }
    &.--close {
      height: 12px;
      width: 12px;
    }
  }
  &.--focused {
    border-color: var(--bg-action);
  }
}

.search-input {
  height: 26px;
  width: 100%;
  border: none;
  @include font-size(13px);
  background: transparent;
  color: var(--fg-primary);
  &:focus-visible {
    outline: 0;
  }
  @include input-placeholder {
    color: var(--fg-tertiary);
  }
}
</style>
