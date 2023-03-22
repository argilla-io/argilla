<template>
  <div class="user-token">
    <h2
      class="user-token-item --heading5 --semibold description__title"
      v-html="title"
    />
    <p class="user-token-item --body1 description__text" v-html="description" />

    <div class="user-token-item token-and-copy-button">
      <span v-html="userToken" />

      <BaseButton
        title="Copy to clipboard"
        class="secondary small"
        @click.prevent="$copyToClipboard(userToken)"
      >
        Copy token
      </BaseButton>
    </div>
  </div>
</template>

<script>
export default {
  name: "UserTokenComponent",
  props: {
    userToken: {
      type: String,
      required: true,
    },
  },
  created() {
    this.title = "Personal access tokens";
    this.description = `Personal access tokens allow you to access your own data via the API.
                            Do not give out your personal access tokens to anybody who do you
                        don't want to access your files.`;
  },
};
</script>

<style lang="scss" scoped>
.user-token {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 16px;
  _text {
    color: $black-37;
  }
  .user-token-item:not(:last-child) {
    width: 80%;
  }
}
.token-and-copy-button {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
