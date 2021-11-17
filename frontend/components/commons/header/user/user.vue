<template>
  <div class="user" v-click-outside="close" v-if="$auth.loggedIn">
    <a class="user__button"
    href="#"
    @click.prevent="showSelector()"
    >
    {{firstChar(user.current_workspace ? user.current_workspace : user.username )}}
    </a>
    <div v-if="visibleSelector && user" class="user__content">
      <p class="user__mail">{{user.email}}</p>
      <a href="#" @click="selectWorkspace(user.username)" class="user__workspace">
        <div class="user__workspace__circle private">{{firstChar(user.username)}}</div>
        <p class="user__workspace__name">{{user.username}}<span>Private Workspace</span></p>
      </a>
      <a href="#" @click="selectWorkspace(workspace)" class="user__workspace" v-for="workspace in user.workspaces" :key="workspace">
        <div class="user__workspace__circle">{{firstChar(workspace)}}</div>
        <p class="user__workspace__name">{{workspace}}<span>Team workspace</span></p>
      </a>
      <a class="user__logout"
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
      visibleSelector: false
    };
  },
  computed: {
    user() {
      return this.$auth.user;
    }
  },
  methods: {
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
    async selectWorkspace(workspace) {
      this.$auth.setUser({ ...this.user, current_workspace: workspace });
    }
  }
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
    top: 3em;
    right: 0;
    background: $lighter-color;
    border-radius: 3px;
    @include font-size(12px);
    font-weight: 600;
    color: palette(grey, medium);
    padding: 1.2em;
    box-shadow: 0 2px 5px 0 rgba(0, 0, 0, 0.5);
    min-width: 200px;
    a {
      text-decoration: none;
    }
  }
  &__mail {
    margin-bottom: 1em;
    margin-top: 0;
  }
  &__logout {
    @include font-size(14px);
  }
  &__workspace {
    display: flex;
    align-items: center;
    margin-bottom: 1em;
    outline: none !important;
    &__circle {
      @extend %circle;
      margin-right: 0.7em;
      background: palette(grey, dark);
      color: $lighter-color;
      &.private {
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
</style>

