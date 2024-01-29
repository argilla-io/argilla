<template>
  <main class="hf-login">
    <div class="hf-login__hero">
      <BrandLogo class="hf-login__logo" />
      <div class="hf-login__hero__content">
        <h1 class="hf-login__title" v-text="$t('login.hf.title', { space })" />
        <h2
          class="hf-login__subtitle"
          v-html="$t('login.hf.subtitle', { user })"
        />
        <div class="hf-login__buttons">
          <HuggingFaceButton class="hf-login__button--hugging-face" />
          <BaseButton
            class="hf-login__button"
            @click="
              $router.replace({
                name: 'sign-in',
                params: { omitCTA: true },
              })
            "
            >{{ $t("button.sign_in_with_username") }}</BaseButton
          >
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

<style lang="scss" scoped>
$bg-color: #f5e3db;
$gradient-bg-color: linear-gradient(178.31deg, #f6d8ca 1.36%, #fbc5ac 109.14%);
.hf-login {
  height: 100vh;
  background: $bg-color;
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
      max-width: 180px;
    }
  }
  &__title {
    margin: 0;
    font-family: $secondary-font-family;
    text-align: center;
    @include font-size(30px);
    line-height: 1.3;
    @include media(">tablet") {
      @include font-size(40px);
    }
  }
  &__subtitle {
    margin: 0;
    text-align: center;
    font-weight: 400;
    @include font-size(22px);
    line-height: 1.3;
    @include media(">tablet") {
      @include font-size(26px);
    }
  }
  &__hero {
    position: relative;
    display: flex;
    flex-direction: column;
    padding: $base-space * 2;
    gap: $base-space * 2;
    @include media(">tablet") {
      padding: $base-space * 5;
    }
    &__content {
      display: flex;
      flex-direction: column;
      gap: $base-space * 3;
      align-items: center;
      margin-top: 10vh;
      @include media(">tablet") {
        margin-top: 3vh;
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
    transition: color 0.2s ease-in;
    @include font-size(16px);
    &:hover {
      color: palette(orange-red-crayola);
      transition: color 0.2s ease-in;
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
    display: flex;
    max-width: min(400px, calc(100% - $base-space * 4));
    padding: $base-space * 2;
    margin: auto;
    background: palette(white);
    border-radius: $border-radius-l;
    box-shadow: 0px 4px 25px rgba(200, 167, 167, 0.5);
    @include media(">tablet") {
      position: relative;
      max-width: min(74%, 1400px);
    }
  }
  &__img {
    width: 100%;
    border-radius: $border-radius;
  }
}
</style>
