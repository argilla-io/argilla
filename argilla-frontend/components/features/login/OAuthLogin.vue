<template>
  <div class="oauth__container" v-if="providers.length">
    <BaseSeparator />
    <ul class="oauth__container__providers">
      <li v-for="provider in providers" :key="provider.name">
        <HuggingFaceButton
          v-if="provider.isHuggingFace"
          @click="authorize(provider.name)"
        />
        <OAuthLoginButton
          v-else
          :provider="provider.name"
          @click="authorize(provider.name)"
        />
      </li>
    </ul>
  </div>
</template>

<script>
import { useOAuthLoginViewModel } from "./useOAuthLoginViewModel";

export default {
  name: "OAuthLogin",
  setup() {
    return useOAuthLoginViewModel();
  },
};
</script>

<style lang="scss" scoped>
.oauth {
  &__container {
    margin-top: $base-space * 3;
    display: flex;
    flex-direction: column;
    gap: $base-space * 3;
    &__providers {
      display: flex;
      flex-direction: column;
      gap: $base-space;
      justify-content: center;
      padding: 0;
      list-style: none;
    }
  }
}
</style>
