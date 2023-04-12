<template>
  <div class="sidebar"></div>
</template>

<script>
export default {};
</script>

<style lang="scss" scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  gap: 1em;
  border-left: 1px solid #e6e6e6;
  background: #f5f5f5;
  pointer-events: all;
  transition: box-shadow 0.2s ease-in-out 0.4s;
}
</style>
