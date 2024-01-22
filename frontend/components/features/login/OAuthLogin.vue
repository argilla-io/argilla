<template>
  <div class="oauth--container">
    <BaseSeparator />

    <HuggingFaceButton />
  </div>
</template>
<script>
export default {
  name: "OAuthLogin",
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
