<template>
  <div class="topbar">
    <RubrixIsotipo v-if="!title" />
    <NuxtLink v-else :to="{ name: 'datasets' }">
      <p class="title">
        {{ title }}
      </p>
    </NuxtLink>
    <slot />
    <ReButton
      v-if="$auth.loggedIn && $config.securityEnabled"
      class="topbar__logout"
      @click="logout"
      >Close session</ReButton
    >
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: undefined,
    },
    icon: {
      type: String,
      default: undefined,
    },
  },
  data: () => ({}),
  methods: {
    async logout() {
      await this.$auth.logout();
      await this.$auth.strategy.token.reset();
    },
  },
};
</script>

<style lang="scss" scoped>
.topbar {
  width: 100%;
  display: flex;
  align-items: center;
  min-height: 60px;
  position: relative;
  background: $primary-color;
  border-bottom: 1px solid $line-light-color;
  color: $lighter-color;
  @extend %container;
  padding-top: 0;
  padding-bottom: 0;
  &__logout {
    @include font-size(15px);
    color: $lighter-color;
    margin: auto 0 auto 1em;
    min-height: none;
    text-transform: normal;
    border: none;
    background: none;
    outline: none;
    cursor: pointer;
  }
  a {
    text-decoration: none;
  }
  .title {
    color: $lighter-color;
    @include font-size(18px);
    font-weight: 900;
    font-family: $ff;
    text-decoration: none;
    .svg-icon {
      margin-right: 0.5em;
    }
  }
}
</style>
