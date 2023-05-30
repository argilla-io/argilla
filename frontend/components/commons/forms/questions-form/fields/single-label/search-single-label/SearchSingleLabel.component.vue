<template>
  <div class="search-area" @click="focusInSearch">
    <BaseIconWithBadge
      class="icon-search"
      icon="search"
      :show-badge="false"
      iconColor="#acacac"
      badge-vertical-position="top"
      badge-horizontal-position="right"
      badge-border-color="white"
    />
    <input
      class="search-input"
      type="text"
      :value="value"
      :ref="$attrs.searchRef"
      :placeholder="$attrs.placeholder"
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
  name: "SearchSingleLabelComponent",
  props: {
    value: {
      type: String,
      default: () => "",
    },
  },
  methods: {
    looseFocus() {
      this.$refs[this.$attrs.searchRef].blur();
    },
    focusInSearch() {
      this.$refs[this.$attrs.searchRef].focus();
    },
  },
};
</script>

<style lang="scss" scoped>
.search-area {
  display: flex;
  align-items: center;
  width: 14.5em;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 10px;
  .icon-search {
    padding: 0;
    background: transparent;
  }
  &:hover {
    box-shadow: 0 6px 10px 0 rgba(0, 0, 0, 0.1);
  }
}

.search-input {
  height: $base-space * 4;
  width: 100%;
  border: none;
  border-radius: 10px;
  &:focus-visible {
    outline: 0;
  }
}
</style>
