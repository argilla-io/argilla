<template>
  <div v-if="$auth.loggedIn" v-click-outside="close" class="user">
    <a
      class="user__button"
      @click.prevent="showSelector"
      role="button"
      aria-label="User Button"
    >
      {{ user.avatar }}
    </a>
    <div v-if="visibleSelector && user" class="user__content">
      <div class="head">
        <div class="left-head">
          <span v-circle v-text="user.avatar" />
        </div>
        <div class="right-head">
          <div class="item">
            <span v-text="user.userName" />
          </div>
          <div class="item" v-if="user.email">
            <span v-text="user.email" />
          </div>
        </div>
      </div>
      <div class="" role="list">
        <NuxtLink class="user__link" :to="{ name: 'user-settings' }">
          {{ $t("userAvatarTooltip.settings") }}
        </NuxtLink>
        <a
          class="user__link"
          :href="$config.documentationSite"
          target="_blank"
          v-text="$t('userAvatarTooltip.docs')"
        />
        <a
          class="user__link"
          @click.prevent="logout"
          v-text="$t('userAvatarTooltip.logout')"
        />
      </div>
      <span class="copyright"
        >© {{ currentYear }} Argilla ({{ $config.clientVersion }})</span
      >
    </div>
  </div>
</template>

<script>
import "assets/icons/external";
import "assets/icons/log-out";

import { useAvatarTooltipViewModel } from "./userAvatarTooltipViewModel";

export default {
  data: () => {
    return {
      visibleSelector: false,
      appVersion: undefined,
    };
  },
  computed: {
    currentYear() {
      return new Date().getFullYear();
    },
  },
  methods: {
    showSelector() {
      this.visibleSelector = !this.visibleSelector;
    },
    close() {
      this.visibleSelector = false;
    },
    async logout() {
      await this.$auth.logout();

      this.goToSignIn();
    },
  },
  setup() {
    return useAvatarTooltipViewModel();
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
  padding: $base-space $base-space * 2 $base-space * 2 $base-space * 2;
  border-bottom: 1px solid hsl(from var(--color-white) h s l / 10%);
  .right-head {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

.user {
  position: relative;
  margin-left: auto;
  z-index: 3;
  &__button {
    user-select: none;
    cursor: pointer;
    @extend %circle;
    background: var(--color-brand);
    transform: scale3d(1, 1, 1) translateZ(0);
    transition: all 0.2s ease-in-out;
    color: var(--color-white);
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
    padding-top: $base-space * 2;
    background: var(--color-dark-grey);
    border-radius: $border-radius;
    @include font-size(14px);
    font-weight: 400;
    color: var(--color-white);
    box-shadow: $shadow;
    min-width: 260px;
    &:after {
      position: absolute;
      top: -10px;
      right: 1em;
      @include triangle(top, 10px, 10px, var(--color-dark-grey));
    }
    a {
      text-decoration: none;
    }
  }
  &__link {
    user-select: none;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    padding: $base-space * 2 $base-space * 2 $base-space * 2 $base-space * 2;
    color: hsl(from var(--color-white) h s l / 80%);
    a {
      color: hsl(from var(--color-white) h s l / 80%);
    }
    &:hover {
      color: var(--color-white);
      .svg-icon {
        color: var(--color-white);
      }
    }
  }
  &__link:not(:last-child) {
    border-bottom: 1px solid hsl(from var(--color-white) h s l / 10%);
  }
}

.copyright {
  display: block;
  @include font-size(11px);
  font-weight: 400;
  line-height: 1em;
  padding: 1em;
  background: rgba(0, 0, 0, 0.54);
  text-align: right;
  border-bottom-right-radius: $border-radius;
  border-bottom-left-radius: $border-radius;
}
</style>
