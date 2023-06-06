<template>
  <div class="search-area" @click="focusInSearch">
    <BaseIconWithBadge
      class="icon-search"
      :class="value?.length ? '--close' : '--search'"
      :icon="value?.length ? 'close' : 'search'"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
      @click-icon="resetValue"
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
  methods: {
    looseFocus() {
      this.$refs[this.searchRef].blur();
    },
    focusInSearch() {
      this.$refs[this.searchRef].focus();
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
  .icon-search {
    padding: 0;
    background: transparent;
    width: 20px;
    height: 20px;
    transition: none;
    &.--search {
      cursor: default;
    }
    &.--close {
      padding: 2px;
    }
  }
  &:hover {
    border-color: $black-20;
  }
}

.search-input {
  height: 28px;
  width: 100%;
  border: none;
  border-radius: 10px;
  &:focus-visible {
    outline: 0;
  }
}
</style>
