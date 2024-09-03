<template>
  <section class="auth__wrapper">
    <div class="auth__info">
      <DecorationShape />
      <h1 class="auth__info__claim">
        <slot name="claim">
          <span v-html="$t('login.claim')" />
        </slot>
      </h1>
    </div>
    <div class="auth__form">
      <BrandLogo class="auth__form__logo" />
      <div class="auth__form__content">
        <slot></slot>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: "AuthenticationLayout",
};
</script>

<style lang="scss" scoped>
.auth {
  &__wrapper {
    display: flex;
    background: var(--bg-accent-grey-1);
    min-height: 100vh;
  }
  &__info {
    position: relative;
    display: none;
    overflow: hidden;
    @include media(">desktop") {
      background: linear-gradient(178.31deg, #ffe5d9 1.36%, #ffd1bc 109.14%);
      padding: $base-space * 2;
      display: flex;
      align-items: flex-start;
      justify-content: left;
      width: 60vw;
    }
    &__claim {
      position: relative;
      font-family: $secondary-font-family;
      color: var(--color-black);
      @include font-size(30px);
      line-height: 1.2em;
      @include media(">desktop") {
        font-size: clamp(40px, 3vw, 60px);
        padding-left: 12%;
        padding-top: $base-space * 12;
        text-wrap: balance;
      }
      &--mobile {
        position: relative;
        color: var(--color-black);
        max-width: 260px;
        margin: 0;
        @include font-size(20px);
        line-height: 1.2;
        font-family: $secondary-font-family;
        @include media(">desktop") {
          display: none;
        }
      }
    }
    &--mobile {
      position: relative;
      height: 160px;
      display: flex;
      align-items: flex-end;
      flex-shrink: 0;
      @include media(">desktop") {
        display: none;
      }
    }
  }
  &__form {
    display: flex;
    flex-direction: column;
    gap: $base-space * 5;
    justify-content: space-between;
    flex: 1;
    height: 100vh;
    padding: $base-space * 2;
    overflow: auto;
    @include media(">desktop") {
      padding: $base-space * 4;
    }
    &__content {
      width: 100%;
      max-width: 400px;
      margin: auto;
    }
    &__logo {
      text-align: left;
      max-width: 120px;
      height: auto;
      flex-shrink: 0;
      @include media(">desktop") {
        max-width: 180px;
      }
    }
    &__claim {
      @include media(">tablet") {
        display: none;
      }
    }
  }
}
:deep(.form) {
  display: flex;
  flex-direction: column;
  gap: $base-space * 2;
}
:deep(.form__title) {
  display: flex;
  align-items: center;
  gap: $base-space * 2;
  font-family: $secondary-font-family;
  @include font-size(30px);
  line-height: 1.2em;
  margin: 0;
  @include media(">desktop") {
    @include font-size(36px);
  }
}
:deep(.form__subtitle) {
  @include font-size(18px);
  line-height: 1.4em;
  font-weight: 400;
  margin: 0;
}
:deep(.form__text) {
  @include font-size(16px);
  line-height: 1.4em;
  margin: 0;
}
:deep(.form__button.button) {
  @include font-size(16px);
  padding: $base-space * 2;
}
:deep(.form__link.button) {
  display: inline-flex;
  padding: 0;
  @include font-size(16px);
  line-height: 1.2;
  font-weight: 400;
}
:deep(.form__terms) {
  @include font-size(12px);
  margin: 0;
  a {
    color: var(--bg-action);
    text-decoration: none;
    &:hover {
      color: var(--bg-action-accent);
    }
  }
}
:deep(.form__error) {
  color: var(--color-brand);
}
:deep(.form__extra-info) {
  @include font-size(14px);
  margin-bottom: 0;
  a {
    color: var(--bg-action);
    text-decoration: none;
    &:hover {
      color: var(--bg-action-accent);
    }
  }
}
</style>
