<template>
  <div class="wrapper">
    <div class="loading-state" v-if="$fetchState.pending">
      Fetching user info
    </div>

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
// import { ObservationDataset } from "@/models/Dataset";

export default {
  name: "LeftUserSettingsContent",
  data() {
    return {
      user: null,
    };
  },
  async fetch() {
    await this.fetchUserInfo();
  },
  methods: {
    async fetchUserInfo() {
      // fetch original data
      //   try {
      //     const { response } = await ObservationDataset.api().get("me");
      //     console.log(response.data);
      //   } catch (err) {
      //     console.log(err);
      //   }

      // fetch mocking data
      let user = null;
      try {
        const data = await fetch("http://localhost:4000/me");
        if (data.ok) {
          user = await data.json();
          this.user = user;
        }
      } catch (err) {
        console.log(err);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.left-content-item {
  border-bottom: 1px solid $black-10;
}
</style>
