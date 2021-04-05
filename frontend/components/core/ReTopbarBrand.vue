<template>
  <div class="topbar">
    <BiomeIsotipo v-if="!title" />
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
      >Logout</ReButton
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
    referer: {
      type: Object,
      required: true,
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
  background: $lighter-color;
  border-bottom: 1px solid $line-light-color;
  font-family: $sff;
  color: $lighter-color;
  padding-left: 2em;
  &__logout {
    margin: auto 1em auto 1em;
    min-height: none;
    color: $primary-color;
    text-transform: normal;
    border: none;
    background: none;
    outline: none;
    cursor: pointer;
    &:hover {
      color: darken($primary-color, 10%);
    }
  }
  a {
    text-decoration: none;
  }
  .title {
    @include font-size(18px);
    font-weight: 900;
    font-family: $ff;
    color: $lighter-color;
    text-decoration: none;
    .svg-icon {
      margin-right: 0.5em;
    }
  }
}
</style>
