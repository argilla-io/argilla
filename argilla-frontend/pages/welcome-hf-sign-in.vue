<template>
  <main class="hf-login">
    <BaseLoading v-if="!isHuggingFaceConfigured || !user || !space" />
    <div v-else class="hf-login__hero">
      <BrandLogo color="dark" class="hf-login__logo" />
      <div class="hf-login__hero__content">
        <h1 class="hf-login__title" v-text="$t('login.hf.title', { space })" />
        <h2
          class="hf-login__subtitle"
          v-html="$t('login.hf.subtitle', { user })"
        />
        <div class="hf-login__buttons">
          <HuggingFaceButton
            class="hf-login__button--hugging-face"
            @click="authorize"
          />
          <BaseButton class="hf-login__button" @click="goToLogin">{{
            $t("button.sign_in_with_username")
          }}</BaseButton>
        </div>
      </div>
    </div>

    <div class="hf-login__img-container">
      <img
        class="hf-login__img"
        src="images/welcome-hf-sign-in-ss.png"
        alt="argilla UI"
      />
    </div>
  </main>
</template>
<script>
import { useWelcomeHFViewModel } from "./useWelcomeHFViewModel";

export default {
  name: "hf-login",
  data() {
    return {
      user: "",
      space: "",
      isHuggingFaceConfigured: false,
    };
  },
  methods: {
    goToLogin() {
      this.$router.replace({
        name: "sign-in",
        params: { omitCTA: true },
        query: this.$route.query,
      });
    },
  },
  async beforeMount() {
    this.isHuggingFaceConfigured = await this.hasHuggingFaceOAuthConfigured();

    if (!this.isHuggingFaceConfigured) {
      this.goToLogin();
    }

    const huggingFaceSpaceInfo = await this.getHuggingFaceSpace();

    if (!huggingFaceSpaceInfo) {
      return this.goToLogin();
    }

    this.user = huggingFaceSpaceInfo.user;
    this.space = huggingFaceSpaceInfo.space;
  },
  setup() {
    return useWelcomeHFViewModel();
  },
};
</script>

<style lang="scss" scoped>
$bg-color: var(--bg-auth);
$gradient-bg-color: var(--bg-auth-gradient);
.hf-login {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: $bg-color;
  color: var(--color-black);
  &:before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    min-height: 100%;
    width: 100%;
    background: $gradient-bg-color;
    @include media(">tablet") {
      min-height: 70vh;
    }
  }
  &__logo {
    max-width: 120px;
    height: auto;
    line-height: 1.3;
    @include media(">tablet") {
      max-width: 200px;
    }
  }
  &__title {
    margin: 0;
    font-family: $secondary-font-family;
    text-align: center;
    @include font-size(30px);
    line-height: 1.2;
    @include media(">tablet") {
      @include font-size(46px);
    }
  }
  &__subtitle {
    margin: 0;
    text-align: center;
    font-weight: 400;
    @include font-size(20px);
    line-height: 1.2;
    @include media(">tablet") {
      @include font-size(24px);
    }
  }
  &__hero {
    position: relative;
    display: flex;
    height: 100%;
    flex-direction: column;
    padding: $base-space * 2;
    gap: $base-space * 2;
    @include media(">tablet") {
      padding: $base-space * 5 $base-space * 5 $base-space * 2 $base-space * 5;
    }
    &__content {
      display: flex;
      height: 80%;
      flex-direction: column;
      justify-content: center;
      gap: $base-space * 2;
      align-items: center;
      @include media(">desktop") {
        gap: $base-space * 3;
        height: 100%;
      }
    }
  }
  &__buttons {
    display: flex;
    flex-direction: column;
    gap: $base-space;
  }
  &__button.button {
    justify-content: center;
    transition: opacity 0.2s ease-in;
    @include font-size(16px);
    color: var(--color-black);
    &:hover {
      opacity: 0.8;
      transition: opacity 0.2s ease-in;
    }
  }
  &__button--hugging-face {
    margin: auto;
    padding: $base-space * 1.1;
    @include font-size(16px);
    @include media(">tablet") {
      @include font-size(18px);
    }
  }
  &__img-container {
    position: fixed;
    bottom: -24px;
    left: 0;
    right: 0;
    max-width: min(400px, calc(100% - $base-space * 4));
    padding: $base-space;
    margin-inline: auto;
    background: var(--color-white);
    border-radius: 18px;
    @include media(">tablet") {
      position: relative;
      padding: $base-space * 2;
      max-width: min(74%, 1240px);
    }
  }
  &__img {
    width: 100%;
    border-radius: 8px;
  }
}
</style>
