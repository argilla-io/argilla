<template>
  <div class="wrapper">
    <BaseSpinner v-if="!user" />

    <div class="left-content" v-if="user">
      <div class="left-content-item edition-user-info-component">
        <EditionUserInfoComponent :userInfo="user" />
      </div>
      <div class="left-content-item user-token-component">
        <UserTokenComponent :userToken="user.api_key" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "LeftUserSettingsContent",
  computed: {
    user() {
      return this.$auth.user;
    },
  },
};
</script>

<style lang="scss" scoped>
.left-content-item {
  border-bottom: 1px solid $black-10;
}
</style>
