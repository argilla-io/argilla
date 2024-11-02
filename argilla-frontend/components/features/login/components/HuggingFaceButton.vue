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
  background: var(--color-black);
  color: var(--color-white);
  width: 100%;
  padding: calc($base-space / 2) $base-space * 4;
  justify-content: center;
  &:hover {
    background: hsl(from var(--color-black) h s l / 80%);
  }
  svg {
    width: 30px;
    height: auto;
  }
}
</style>
