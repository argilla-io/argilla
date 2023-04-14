<template>
  <div class="layout">
    <div class="header-area">
      <slot name="header">here is the header</slot>
    </div>
    <div class="empty-content-left"></div>
    <div class="footer-area">
      <slot name="footer">here is the footer</slot>
    </div>
    <div class="sidebar-area">
      <slot name="sidebar-right">here is the sidebar content left</slot>
    </div>
    <div class="empty-content-right"></div>
    <div class="top-area">
      <slot name="top">here is the top content</slot>
    </div>
    <div class="center-area">
      <slot name="center">here is the center content</slot>
    </div>
  </div>
</template>

<script>
export default {
  name: "HeaderAndTopAndOneColumnsLayout",
};
</script>

<style lang="scss" scoped>
.layout {
  display: grid;
  grid-template-columns: 56px 1fr 56px auto;
  grid-template-rows: auto 100px 1fr auto;
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  height: 100vh;
}

.header-area {
  grid-area: 1 / 1 / 2 / 6;
}
.empty-content-left {
  grid-area: 2 / 1 / 4 / 2;
}
.footer-area {
  grid-area: 4 / 1 / 5 / 4;
}
.sidebar-area {
  grid-area: 2 / 4 / 5 / 5;
}
.empty-content-right {
  grid-area: 2 / 3 / 4 / 4;
}
.top-area {
  grid-area: 2 / 2 / 3 / 3;
}
.center-area {
  grid-area: 3 / 2 / 4 / 3;
  overflow-x: hidden;
}
</style>
