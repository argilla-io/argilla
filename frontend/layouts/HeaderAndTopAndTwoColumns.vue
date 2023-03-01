<template>
  <div class="layout">
    <div class="header">here is the header</div>
    <div class="top">
      <slot name="top">here is the top content</slot>
    </div>
    <div class="left">
      <slot name="left">here is the left content</slot>
    </div>
    <div class="right">
      <slot name="right">here is the right content</slot>
    </div>
  </div>
</template>

<script>
export default {
  name: "HeaderAndTopAndTwoColumnsLayout",
};
</script>

<style lang="scss" scoped>
.layout {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: 50px 100px 1fr;
  grid-column-gap: 0px;
  grid-row-gap: 10px;
}
.header {
  grid-area: 1 / 1 / 2 / 3;
}
.top {
  grid-area: 2 / 1 / 3 / 3;
}
.right {
  grid-area: 3 / 2 / 4 / 3;
}
.left {
  grid-area: 3 / 1 / 4 / 2;
}
</style>
