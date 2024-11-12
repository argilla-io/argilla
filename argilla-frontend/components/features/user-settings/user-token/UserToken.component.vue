<template>
  <div class="user-token">
    <h2
      class="user-token-title --heading5 --medium description__title"
      v-text="$t('userSettings.apiKey')"
    />
    <p
      class="user-token-description --body1 description__text"
      v-text="$t('userSettings.apiKeyDescription')"
    />

    <span class="user-token-value --body1" v-text="'**** **** **** ****'" />

    <div class="user-token-button">
      <base-action-tooltip :tooltip="$t('copied')">
        <BaseButton
          :title="$t('button.tooltip.copyToClipboard')"
          class="secondary small"
          @click.prevent="$copyToClipboard(userToken)"
        >
          {{ $t("userSettings.copyKey") }}
        </BaseButton>
      </base-action-tooltip>
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
  grid-gap: $base-space;
  padding: $base-space * 3 0;
}

.user-token-title {
  grid-area: a;
  margin: 0;
}
.user-token-description {
  grid-area: b;
  color: var(--fg-tertiary);
  margin-top: 0;
}
.user-token-value {
  grid-area: c;
  word-break: break-word;
}
.user-token-button {
  grid-area: d;
  margin-left: auto;
}
</style>
