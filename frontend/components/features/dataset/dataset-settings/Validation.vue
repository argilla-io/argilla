<template>
  <div>
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
.--error-message {
  @include font-size(12px);
  color: palette(orange-red-crayola);
}
</style>
