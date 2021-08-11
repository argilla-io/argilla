<template>
  <aside :class="['sidebar', annotationEnabled ? 'annotation' : 'explore']">
    <div class="sidebar__wrapper">
      <div class="sidebar__content">
        <slot></slot>
      </div>
    </div>
  </aside>
</template>
<script>
export default {
  props: {
    dataset: {
      type: Object,
      required: true,
    },
  },
  computed: {
    annotationEnabled() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },
};
</script>
<style lang="scss" scoped>
.sidebar {
  z-index: 2;
  &__wrapper {
    min-height: 300px;
    border-radius: 5px;
    width: 280px;
    position: absolute;
    right: 3em;
    background: white;
    padding: 1em 2em;
    box-shadow: 0 5px 11px 0 rgba(0, 0, 0, 0.5);
    overflow: auto;
    transition: top 0.2s ease-in-out;
    .TextClassification & {
      max-height: calc(100vh - 180px);
    }
    .TokenClassification & {
      max-height: calc(100vh - 260px);   
    }
    .annotation & {
      margin-top: -4.5em;
    }
    .explore & {
      margin-top: 1em;
    }
    .fixed-header .TextClassification & {
      max-height: calc(100vh - 160px);
      margin-top: 1em;
    }
    .fixed-header .TokenClassification & {
      max-height: calc(100vh - 260px);
      margin-top: 1em;
    }
    @include media(">desktopLarge") {
      margin-left: 1em;
      margin-top: 1em;
      display: block !important;
      position: relative;
      right: 0;
    }
  }
  &__content {
    border-radius: 2px;
    @include font-size(13px);
    &:first-child {
      padding-top: 0;
    }
    p {
      display: flex;
      align-items: flex-end;
      @include font-size(18px);
      margin-top: 0;
      margin-bottom: 2em;
      font-weight: 600;
      svg {
        margin-right: 1em;
      }
    }
  }
}
</style>
