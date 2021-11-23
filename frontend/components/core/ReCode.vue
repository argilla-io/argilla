<template>
  <pre>
    <code v-highlight class="python"><slot></slot></code>
  </pre>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped>
.hljs {
  margin: 0;
  background-color: #333346;
  color: white;
  padding: 1em !important;
  border-radius: 5px;
  text-align: left;
  @include font-size(13px);
}
</style>

