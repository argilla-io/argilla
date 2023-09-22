<template>
  <div class="badge">
    <p class="badge__text" v-if="!clickable" v-html="text" />
    <BaseButton class="badge__text" @click="onClick" v-else>{{
      text
    }}</BaseButton>
    <BaseButton v-if="clearable" class="badge__close-button" @click="onClear()">
      <svgicon
        class="badge__close-button__icon"
        name="close"
        width="12"
        height="12"
    /></BaseButton>
  </div>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      clickable: false,
      clearable: false,
    };
  },
  mounted() {
    if (this.$listeners["on-click"]) {
      this.clickable = true;
    }
    if (this.$listeners["on-clear"]) {
      this.clearable = true;
    }
  },
  methods: {
    onClick() {
      this.$emit("on-click");
    },
    onClear() {
      this.$emit("on-clear");
    },
  },
};
</script>

<style lang="scss" scoped>
.badge {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: calc($base-space / 2) $base-space;
  border: 1px solid $black-37;
  border-radius: $border-radius-rounded;
  background-color: #ffe9cd;
  @include font-size(12px);
  @include line-height(12px);
  &__text {
    margin: 0;
  }
  &__close-button {
    padding: 0;
    flex-shrink: 0;
    &__icon {
      min-width: 12px;
    }
  }
}
</style>
