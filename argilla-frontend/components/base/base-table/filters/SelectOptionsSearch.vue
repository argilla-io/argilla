<template>
  <div class="options-search">
    <input
      v-model="searchText"
      class="options-search__input"
      type="text"
      autofocus
      :placeholder="$t('search')"
    />
    <a href="#" class="options-search__clear" @click.prevent="clear">
      <svgicon
        v-if="allowClear && !!searchText"
        name="close"
        width="10"
        height="10"
        color="#9b9b9b"
      ></svgicon>
    </a>
  </div>
</template>

<script>
export default {
  props: {
    value: {
      type: String,
      default: "",
    },
    allowClear: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    searchText: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      },
    },
  },
  methods: {
    clear() {
      this.$emit("clear");
    },
  },
};
</script>

<style scoped lang="scss">
.options-search {
  &__input {
    border: none;
    outline: none;
    height: 40px;
    background: transparent;
    width: calc(100% - 20px);
    @include input-placeholder {
      color: var(--fg-tertiary);
    }
  }
  &__clear {
    outline: none;
  }
}
</style>
