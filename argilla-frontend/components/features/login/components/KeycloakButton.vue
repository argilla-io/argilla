<template>
  <BaseButton class="button-kc" @click="$emit('click')">
    <KeycloakLogo />
    {{ $t("button.kc-login") }}
  </BaseButton>
</template>
<script>
export default {
  name: "KeycloakButton",
};
</script>

<style lang="scss" scoped>
.button-kc {
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
