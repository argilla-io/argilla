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
  margin: 0 auto auto 0;
  padding-top: 0;
  padding-bottom: 0;
  padding-left: 4em;
  padding-right: calc(4em + 45px);
  @include media(">desktopLarge") {
    width: 100%;
    padding-right: calc(294px + 45px + 4em)
  }
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
}
</style>
