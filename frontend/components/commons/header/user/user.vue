<template>
  <div v-if="$auth.loggedIn" v-click-outside="close" class="user">
    <a class="user__button" href="#" @click.prevent="showSelector">
      {{ firstChar(user.username) }}
    </a>
    <div v-if="visibleSelector && user" class="user__content">
      <div class="head">
        <div class="left-head">
          <span v-circle v-text="firstChar(user.username)" />
        </div>
        <div class="right-head">
          <div class="item">
            <span v-text="user.username" />
          </div>
          <div class="item" v-if="user.email">
            <span v-text="user.email" />
          </div>
        </div>
      </div>
      <div class="">
        <NuxtLink class="user__link" :to="{ name: 'user-settings' }">
          My settings
        </NuxtLink>
        <a
          class="user__link"
          href="https://docs.argilla.io/en/latest/"
          target="_blank"
          v-text="'View docs'"
        />
        <a
          class="user__link"
          href="#"
          @click.prevent="logout"
          v-text="'Log out'"
        />
      </div>
      <span class="copyright"
        >© {{ currentYear }} Argilla ({{ appVersion }})</span
      >
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
      appVersion: undefined,
    };
  },
  computed: {
    user() {
      return this.$auth.user;
    },
    currentYear() {
      return this.currentDate.getFullYear();
    },
    currentDate() {
      return new Date();
    },
  },
  async fetch() {
    this.appVersion = await this.getAppVersion();
  },
  methods: {
    ...mapActions({
      getAppVersion: "entities/rubrix-info/getAppVersion",
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
  font-weight: 500;
  @include font-size(16px);
}

.head {
  display: flex;
  gap: 25px;
  padding: 0.5em 1.5em 1.5em 1.5em;
  border-bottom: 1px solid palette(grey, 400);
  .right-head {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

.user {
  position: relative;
  z-index: 3;
  &__button {
    @extend %circle;
    background: palette(orange-red-crayola);
    transform: scale3d(1, 1, 1) translateZ(0);
    transition: all 0.2s ease-in-out;
    color: palette(white);
    will-change: auto;
    &:hover {
      transform: scale3d(1.05, 1.05, 1.05) translateZ(0);
      transition: all 0.2s ease-in-out;
      outline: 0;
      border: none;
    }
  }
  &__content {
    position: absolute;
    top: 3.8em;
    right: -0.5em;
    padding-top: 1.5em;
    background: palette(grey, 100);
    border-radius: $border-radius;
    @include font-size(14px);
    font-weight: 400;
    color: palette(white);
    box-shadow: $shadow;
    min-width: 260px;
    &:after {
      position: absolute;
      top: -10px;
      right: 1em;
      @include triangle(top, 10px, 10px, palette(grey, 100));
    }
    a {
      text-decoration: none;
    }
  }
  &__name {
    @include font-size(16px);
    margin: 0 1.5em 0.3em 1.5em;
    font-weight: 600;
  }
  &__mail {
    margin: 0 1.5em 2em 1.5em;
    color: palette(apricot);
  }
  &__link {
    display: flex;
    flex-direction: column;
    padding: 1.5em 1.5em 1.5em 1.5em;
    color: palette(white);
    &:hover {
      color: darken(palette(white), 10%);
      .svg-icon {
        fill: darken(palette(white), 10%);
      }
    }
    a {
      color: palette(white);
    }
  }
  &__link:not(:last-child) {
    border-bottom: 1px solid palette(grey, 400);
  }
}

.copyright {
  display: block;
  @include font-size(11px);
  font-weight: 400;
  line-height: 1em;
  padding: 1em;
  background: $black-54;
  text-align: right;
  border-bottom-right-radius: $border-radius;
  border-bottom-left-radius: $border-radius;
}
</style>
