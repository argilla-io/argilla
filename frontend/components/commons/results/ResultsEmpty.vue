<template>
  <div class="empty">
    <span class="empty__content">
      <h1 class="empty__title">{{ title }}</h1>
    </span>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: "0 results found",
    },
  },
};
</script>

<style lang="scss" scoped>
.empty {
  $this: &;
  text-align: center;
  width: 100%;
  display: flex;
  margin-top: 0;
  height: calc(100vh - 400px);
  #{$this}__content {
    align-items: center;
    margin: auto;
  }
  &__title {
    @include font-size(30px);
    font-weight: 400;
  }
}
</style>
