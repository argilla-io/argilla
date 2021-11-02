<template>
  <div class="user" v-click-outside="close">
    <a class="user__button"
    v-if="$auth.loggedIn"
    href="#"
    @click.prevent="showSelector()"
    >
    {{userFirstChar}}
    </a>
    <div v-if="visibleSelector" class="user__content">
          <a
    href="#"
    @click.prevent="logout()"
    >
    Log out
    </a>
    </div>
  </div>
</template>

<script>
export default {
  data: () => {
    return {
      visibleSelector: false,
    }
  },
  computed: {
    userFirstChar() {
      return this.$auth.user.charAt(0);
    }
  },
  methods: {
    showSelector() {
      this.visibleSelector =! this.visibleSelector;
    },
    close() {
      this.visibleSelector = false;
    }, 
    async logout() {
      await this.$auth.logout();
      await this.$auth.strategy.token.reset();
    }
  }
}
</script>

<style scope lang="scss">
$buttonSize: 30px;
.user {
  position: relative;
  z-index: 3;
  &__button {
    height: $buttonSize;
    width: $buttonSize;
    line-height: $buttonSize;
    display: block;
    text-align: center;
    background: $lighter-color;
    text-transform: uppercase;
    border-radius: 50%;
    text-decoration: none;
    transform: scale3d(1, 1, 1) translateZ(0);
    transition: all 0.2s ease-in-out;
    color: $primary-color;
    font-weight: 700;
    @include font-size(16px);
    will-change: auto;
    &:hover {
      transform: scale3d(1.1, 1.1, 1.1) translateZ(0);
      transition: all 0.2s ease-in-out;
    }
  }
  &__content {
    position: absolute;
    top: 2.5em;
    right: 0;
    background: $lighter-color;
    border-radius: 3px;
    @include font-size(14px);
    color: $secondary-color;
    padding: 0.8em;
    box-shadow: 0 2px 5px 0 rgba(0, 0, 0, 0.5);
    min-width: 130px;
    a {
      text-decoration: none;
    }
  }
}
</style>

