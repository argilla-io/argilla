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
        <svgicon width="16" height="16" name="external"></svgicon> View docs
      </a>
      <a class="user__link" href="#" @click.prevent="logout">
        <svgicon width="16" heigth="16" name="log-out"></svgicon> Log out
      </a>
      <span class="copyright">© 2022 Rubrix ({{ rubrixVersion }})</span>
    </div>
  </div>
</template>

<script>
import { mapActions } from "vuex";
import "assets/icons/external";
import "assets/icons/log-out";
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
    background: palette(white);
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
    top: 3.5em;
    right: -0.5em;
    padding-top: 1.5em;
    background: palette(white);
    border-radius: 5px;
    @include font-size(14px);
    font-weight: 400;
    color: $font-medium;
    box-shadow: $shadow;
    min-width: 300px;
    &:after {
      position: absolute;
      top: -10px;
      right: 1em;
      @include triangle(top, 10px, 10px, white);
    }
    a {
      text-decoration: none;
    }
  }
  &__name {
    color: $font-dark;
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
    color: $font-medium;
    margin: 0.5em 1.5em 1.5em 1.5em;
    &:hover {
      color: darken($font-medium, 10%);
      .svg-icon {
        fill: darken($font-medium, 10%);
      }
    }
    .svg-icon {
      margin-right: 0.5em;
    }
  }
}
.copyright {
  display: block;
  @include font-size(11px);
  font-weight: 400;
  color: $font-dark;
  line-height: 1em;
  margin-top: 1.5em;
  padding: 1em;
  background: #fcfcfc;
  text-align: right;
  border-bottom-right-radius: 5px;
  border-bottom-left-radius: 5px;
}
</style>
