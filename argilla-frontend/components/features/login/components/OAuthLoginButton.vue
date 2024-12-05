<template>
  <BaseButton class="sign-in-button" @click="$emit('click')">
    {{ signinText }}
  </BaseButton>
</template>
<script>
export default {
  name: "OAuthLoginButton",
  props: {
    provider: {
      type: String,
      required: true,
    },
  },
  computed: {
    providerName() {
      return this.provider.charAt(0).toUpperCase() + this.provider.slice(1);
    },
    signinText() {
      return this.$t("button.signin_with_provider", {
        provider: this.providerName,
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.sign-in-button {
  @extend %button !optional;
  background: var(--color-black);
  color: var(--color-white);
  width: 100%;
  min-height: $base-space * 6;
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
