<template>
  <div v-if="showAnnotationMode" class="container">
    <div class="global-actions">
      <slot />
    </div>
  </div>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  data: () => ({}),
  computed: {
    showAnnotationMode() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
};
</script>
<style lang="scss" scoped>
.container {
  @extend %container;
  margin: 0 auto;
  padding: 4em;
  padding-top: 0;
  padding-bottom: 0;
}
.global-actions {
  display: flex;
  align-items: center;
  width: 100%;
  text-align: left;
  padding: 1em 1.4em;
  background: $lighter-color;
  border-radius: 3px;
  position: relative;
  &--exploration {
    position: relative;
  }
  .fixed-header & {
    margin-top: 0;
    padding-top: 0;
    padding-bottom: 0;
    background: $bg;
    border: none;
    min-height: 70px;
  }
  @include media(">desktopLarge") {
    width: calc(100% - 294px);
  }
}
</style>
