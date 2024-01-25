<template>
  <BaseButton class="button-hf" @click="$emit('click')">
    <HFLogo />
    {{ $t("button.hf-login") }}
  </BaseButton>
</template>
<script>
export default {
  name: "HuggingFaceButton",
};
</script>

<style lang="scss" scoped>
.button-hf {
  @extend %button !optional;
  background: $black-87;
  color: palette(white);
  width: 100%;
  padding: calc($base-space / 2) $base-space * 4;
  &:hover {
    background: lighten($black-87, 10%);
  }
  svg {
    width: 30px;
    height: auto;
  }
}
</style>
