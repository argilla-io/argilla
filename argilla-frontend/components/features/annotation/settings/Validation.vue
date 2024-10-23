<template>
  <div :class="validations.length ? '--has-error' : null">
    <slot></slot>
    <template v-if="validations.length">
      <span
        class="--error-message"
        v-for="error in validations"
        :key="error"
        v-html="error"
      />
    </template>
  </div>
</template>

<script>
export default {
  props: {
    validations: {
      type: Array,
      required: true,
    },
  },
};
</script>

<style lang="scss" scoped>
$color-error: var(--color-brand);
.--error-message {
  display: block;
  @include font-size(12px);
  color: $color-error;
}
.--has-error {
  input,
  textarea {
    border: 1px solid $color-error;
    &:focus {
      border-color: $color-error;
    }
  }
}
</style>
