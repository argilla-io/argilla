<template>
  <ReInputContainer class="searchbar">
    <ReInput v-model="filter" placeholder="Search datasets" />
    <svgicon v-if="!filter" name="search" width="20" height="40" />
    <svgicon
      v-else
      class="searchbar__button"
      name="cross"
      width="14"
      height="14"
      @click="filter = undefined"
    />
  </ReInputContainer>
</template>
<script>
import "assets/icons/search";
import "assets/icons/cross";

export default {
  data() {
    return { filter: this.value };
  },
  watch: {
    filter(val) {
      this.$emit("input", val);
    },
  },
};
</script>
<style lang="scss" scoped>
.searchbar {
  background: $lighter-color;
  width: 285px;
  min-height: 43px;
  border: none;
  padding: 0 1em;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  margin-right: auto;
  margin-left: 0;
  pointer-events: all;
  border-radius: 5px;
  @include font-size(14px);
  .svg-icon {
    fill: $primary-color;
    margin: auto;
  }
  &__button {
    cursor: pointer;
  }
}
</style>
