<template>
  <div v-if="$auth.loggedIn" v-click-outside="close" class="user">
    <a class="user__button" href="#" @click.prevent="showSelector">
      {{ firstChar(user.username) }}
    </a>
    <div v-if="visibleSelector && user" class="user__content">
      <p class="user__name">{{ user.username }}</p>
      <p class="user__mail">{{ user.email }}</p>
      <a
        class="user__link"
        href="https://docs.rubrix.ml/en/stable/"
        target="_blank"
      >
        <svgicon name="docs"></svgicon> View docs
      </a>
      <a class="user__link" href="#" @click.prevent="logout">
        <svgicon name="logout"></svgicon> Log out
      </a>
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
      return name.slice(0, 2);
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
$buttonSize: 34px;
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
      transform: scale3d(1.05, 1.05, 1.05) translateZ(0);
      transition: all 0.2s ease-in-out;
    }
  }
  &__content {
    position: absolute;
    top: 3.8em;
    right: -1em;
    padding-top: 1.5em;
    background: $lighter-color;
    border-radius: $border-radius;
    @include font-size(12px);
    font-weight: 600;
    color: palette(grey, medium);
    padding: 1.2em 1.2em 0.8em 1.2em;
    box-shadow: $shadow;
    min-width: 200px;
    a {
      text-decoration: none;
    }
  }
  &__name {
    color: palette(grey, dark);
    @include font-size(16px);
    margin: 0 1.5em 0.3em 1.5em;
    font-weight: 600;
  }
  &__mail {
    margin: 0 1.5em 2em 1.5em;
  }
  &__link {
    display: flex;
    align-items: center;
    outline: none !important;
    padding: 0.7em;
    margin: 0 -0.5em 0 -0.5em;
    transition: background-color 0.3s ease-in-out;
    border-radius: $border-radius;
    &:hover {
      background: #f5f5f5;
      transition: background-color 0.3s ease-in-out;
    }
    &__circle {
      @extend %circle;
      margin-right: 0.7em;
      background: palette(grey, dark);
      color: $lighter-color;
      &.active {
        background: $primary-color;
      }
    }
    &__name {
      color: palette(grey, dark);
      margin-top: 0;
      margin-bottom: 0;
      line-height: 1.4em;
      span {
        display: block;
        margin-top: 0;
        margin-bottom: 0;
        color: palette(grey, medium);
      }
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
  text-align: right;
  border-bottom-right-radius: 5px;
  border-bottom-left-radius: 5px;
}
</style>
