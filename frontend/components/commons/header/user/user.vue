<template>
  <div v-if="$auth.loggedIn" v-click-outside="close" class="user">
    <a
      class="user__button"
      href="#"
      @click.prevent="showSelector"
    >
      {{ firstChar(user.username) }}
    </a>
    <div v-if="visibleSelector && user" class="user__content">
      <p class="user__name">{{ user.username }}</p>
      <p class="user__mail">{{ user.email }}</p>
      <a class="user__link" href="https://docs.rubrix.ml/en/stable/" target="_blank">
        <svgicon name="docs"></svgicon> View docs </a>
      <a class="user__link" href="#" @click.prevent="logout">
        <svgicon name="logout"></svgicon> Log out </a>
      <span class="copyright">© 2022 Rubrix ({{ rubrixVersion }})</span>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import "assets/icons/docs";
import "assets/icons/logout";
export default {
  data: () => {
    return {
      visibleSelector: false,
      rubrixVersion: undefined,
    };
  },
  computed: {
    user() {
      return this.$auth.user;
    },
  },
  async fetch() {
    this.rubrixVersion = await this.getRubrixVersion();
  },
  methods: {
    ...mapActions({
      getRubrixVersion: "entities/rubrix-info/getRubrixVersion",
    }),
    firstChar(name) {
      return name.charAt(0);
    },
    showSelector() {
      this.visibleSelector = !this.visibleSelector;
    },
    close() {
      this.visibleSelector = false;
    },
    async logout() {
      await this.$auth.logout();
      await this.$auth.strategy.token.reset();
    },
  },
};
</script>

<style scope lang="scss">
$buttonSize: 30px;
%circle {
  height: $buttonSize;
  width: $buttonSize;
  line-height: $buttonSize;
  display: block;
  text-align: center;
  text-transform: uppercase;
  border-radius: 50%;
  text-decoration: none;
  font-weight: 700;
  @include font-size(16px);
}
.user {
  position: relative;
  z-index: 3;
  &__button {
    @extend %circle;
    background: $lighter-color;
    transform: scale3d(1, 1, 1) translateZ(0);
    transition: all 0.2s ease-in-out;
    color: $primary-color;
    will-change: auto;
    &:hover {
      transform: scale3d(1.1, 1.1, 1.1) translateZ(0);
      transition: all 0.2s ease-in-out;
    }
  }
  &__content {
    position: absolute;
    top: 3.5em;
    right: 0;
    padding-top: 1em;
    background: $lighter-color;
    border-radius: 3px;
    @include font-size(14px);
    font-weight: 400;
    color: palette(grey, medium);
    box-shadow: 0 2px 5px 0 rgba(0, 0, 0, 0.5);
    min-width: 200px;
    text-align: center;
    a {
      text-decoration: none;
    }
  }
  &__name {
    color: palette(grey, dark);
    @include font-size(16px);
    margin-bottom: 0.5em;
    margin-top: 0;
  }
  &__mail {
    margin-bottom: 1em;
    margin-top: 0;
  }
  &__link {
    display: flex;
    align-items: center;
    margin-top: 0.5em;
    text-align: left;
    color: palette(grey, medium);
    margin-left: 1em;
    .svg-icon {
      margin-right: 0.5em;
    }
  }
}
.copyright {
  display: block;
  @include font-size(11px);
  text-transform: uppercase;
  font-weight: 400;
  color: palette(grey, dark);
  line-height: 1em;
  margin-top: 1.5em;
  padding: 1em;
  background: #fcfcfc;
}
</style>
