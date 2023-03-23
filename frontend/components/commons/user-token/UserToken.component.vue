<template>
  <div class="user-token">
    <h2
      class="user-token-title --heading5 --semibold description__title"
      v-text="title"
    />
    <p
      class="user-token-description --body1 description__text"
      v-text="description"
    />

    <span class="user-token-value" v-text="userToken" />

    <div class="user-token-button">
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
  display: grid;
  grid-template-areas:
    "a ."
    "b ."
    "c d";
  grid-template-columns: 1fr 120px;
  grid-template-rows: auto auto 1fr;
  grid-gap: 5px;
  margin-bottom: 2em;
}

.user-token-title {
  grid-area: a;
}
.user-token-description {
  grid-area: b;
  color: $black-37;
}
.user-token-value {
  grid-area: c;
  word-break: break-word;
}
.user-token-button {
  grid-area: d;
}
</style>
