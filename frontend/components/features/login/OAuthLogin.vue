<template>
  <div class="oauth--container" v-if="providers.length">
    <BaseSeparator />

    <div v-for="provider in providers">
      <HuggingFaceButton
        v-if="provider.isHuggingFace"
        @click="authorize(provider.name)"
      />
    </div>
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
  &--container {
    margin-top: 1em;
    height: fit-content;
    display: flex;
    flex-direction: column;
    gap: 1em;
  }
}
</style>
