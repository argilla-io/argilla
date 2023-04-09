<template>
  <div>
    <div class="header">
      <slot name="header">here is the header</slot>
    </div>
    <main class="layout">
      <div class="empty-content-left"></div>
      <div class="empty-content-right"></div>
      <div class="top">
        <slot name="top">here is the top content</slot>
      </div>
      <div class="left">
        <slot name="left">here is the left content</slot>
      </div>
      <div class="right">
        <slot name="right">here is the right content</slot>
      </div>
    </main>
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
  grid-template-columns: 56px 1fr 1fr 1fr 56px;
  grid-template-rows: 0 100px 1fr 1fr 1fr;
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  overflow: auto;
  height: calc(100vh - $topbarHeight);
  background: palette(white);
}
.header {
  grid-area: 1 / 1 / 2 / 6;
}
.empty-content-left {
  grid-area: 2 / 1 / 6 / 2;
}
.empty-content-right {
  grid-area: 2 / 5 / 6 / 6;
}
.top {
  grid-area: 2 / 2 / 3 / 5;
}
.left {
  grid-area: 3 / 2 / 6 / 4;
}
.right {
  grid-area: 3 / 4 / 6 / 5;
}
</style>
