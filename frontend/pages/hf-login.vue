<template>
  <main class="hf-login">
    <div class="hf-login__hero">
      <BrandLogo class="hf-login__logo" />
      <div class="hf-login__hero__content">
        <h1
          class="hf-login__title"
          v-text="$t('login.hf.title', { space: space })"
        />
        <h2
          class="hf-login__subtitle"
          v-html="$t('login.hf.subtitle', { user: user })"
        />
        <div class="hf-login__buttons">
          <HuggingFaceButton class="hf-login__button--hugging-face" />
          <BaseButton class="hf-login__button">{{
            $t("button.sign_in_with_username")
          }}</BaseButton>
        </div>
      </div>
    </div>

    <div class="hf-login__img-container">
      <img
        class="hf-login__img"
        src="https://docs.argilla.io/en/latest/_images/snapshot-feedback-submitted.png"
        alt="argilla UI"
      />
    </div>
  </main>
</template>
<script>
import { useHuggingFaceHost } from "~/v1/infrastructure/services/useHuggingFaceHost";

export default {
  name: "hf-login",
  data() {
    return {
      user: "user_1",
      space: "space_1",
    };
  },
  mounted() {
    const space = this.isRunningOnHuggingFace();
    this.user = space.user;
    this.space = space.space;
  },
  setup() {
    return useHuggingFaceHost();
  },
};
</script>



