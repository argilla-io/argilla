<template>
  <div class="wrapper">
    <BaseSpinner v-if="!user" />

    <div class="user-settings" v-if="user">
      <div class="user-settings-item edition-user-info-component">
        <EditionUserInfo :userInfo="user" />
      </div>
      <div class="user-settings-item user-token-component">
        <UserTokenComponent :userToken="user.api_key" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserSettingsContent",
  computed: {
    user() {
      return this.$auth.user;
    },
  },
};
</script>

<style lang="scss" scoped>
.user-settings-item {
  border-bottom: 1px solid $black-10;
}
</style>
