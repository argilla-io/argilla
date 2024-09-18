<template>
  <div class="layout">
    <div class="header-area">
      <slot name="header">here is the header</slot>
    </div>
    <div class="center-area">
      <slot name="center">here is the center content</slot>
    </div>
  </div>
</template>

<script>
export default {
  name: "AnnotationPagesLayout",
};
</script>

<style lang="scss" scoped>
$gap-width: $base-space * 2;
.layout {
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto minmax(0, 1fr) auto;
  grid-column-gap: 0px;
  grid-row-gap: 0px;
  grid-template-areas:
    "header"
    "center";
  height: 100vh;
  transition: 0.4s ease-in-out;
  @include media("<desktop") {
    height: 100svh;
  }
}

.header-area {
  grid-area: header;
}
.center-area {
  grid-area: center;
  min-width: 0;
  display: flex;
  flex-direction: column;
  @include media("<desktop") {
    min-height: 0;
  }
}
</style>
