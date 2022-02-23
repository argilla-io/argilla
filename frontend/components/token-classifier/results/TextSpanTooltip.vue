<template>
  <span class="highlight__label">
    <span class="highlight__tooltip__container">
      <span class="highlight__tooltip">
        <span class="highlight__tooltip__origin" v-if="span.origin">{{
          span.origin === "prediction" ? "pred." : "annot."
        }}</span>
        <span>{{ span.entity.label }} </span>
      </span>
    </span>
  </span>
</template>

<script>
export default {
  props: {
    span: {
      type: Object,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.highlight {
  &__label {
    min-height: 40px;
    @include font-size(16px);
    line-height: 20px;
  }
  &__tooltip {
    cursor: default;
    display: block;
    border-radius: 2px;
    padding: 5px 10px 6px 10px;
    margin-bottom: 0.5em;
    transition: opacity 0.5s ease, z-index 0.2s ease;
    white-space: nowrap;
    user-select: none;
    font-weight: 600;
    min-width: 80px;
    @include font-size(16px);
    .prediction & {
      margin-top: 0.5em;
    }
    & > span {
      display: block;
    }
    &__container {
      position: absolute;
      right: 50%;
      transform: translateX(50%);
      opacity: 1;
      transition-delay: 0s;
      z-index: 4;
      .annotation & {
        top: -77px;
      }
      .prediction & {
        top: 13px;
      }
    }
    &__origin {
      @include font-size(12px);
      font-weight: normal;
    }
  }
  &__tooltip:after {
    margin: auto;
    position: absolute;
    right: 0;
    left: 0;
    .annotation & {
      @include triangle(bottom, 6px, 6px, auto);
      bottom: 2px;
    }
    .prediction & {
      @include triangle(top, 6px, 6px, auto);
      top: 3px;
    }
  }
}
</style>
