<template>
  <div class="footer-component">
    <div class="left"></div>
    <div class="center">footer</div>
    <div class="right"></div>
  </div>
</template>

<script>
export default { name: "FooterFeedbackTaskComponent" };
</script>

<style lang="scss" scoped>
.footer-component {
  display: grid;
  grid-template-areas: "a b c";
  grid-template-columns: 56px 1fr 56px;
  grid-template-rows: 56px;
  background: #fafafa;
  border-top: 1px solid #e6e6e6;
}

.left {
  grid-area: a;
}
.center {
  grid-area: b;
}

.right {
  grid-area: c;
}
</style>
