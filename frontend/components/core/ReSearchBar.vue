<template>
  <ReInputContainer class="searchbar">
    <svgicon name="search" width="20" height="30" />
    <ReInput v-model="filter" placeholder="Search" />
  </ReInputContainer>
</template>
<script>
import "assets/icons/search";

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
  background: transparent;
  max-width: 270px;
  border: 1px solid $line-light-color;
  padding: 0 1em;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
  margin: 2em 0 2em auto;
  pointer-events: all;
  @include font-size(14px);
  .svg-icon {
    margin: auto;
    order: 2;
  }
}
</style>
