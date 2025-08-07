<template>
  <div class="top-content" :class="separator ? '--separator' : null">
    <h1 class="--heading2" v-text="$t('settings.title')" />
    <base-button @click="$emit('goToDataset')" class="secondary text">
      <svgicon name="chevron-left" width="10" height="10" />
      {{ $t("settings.seeYourDataset") }}
    </base-button>
  </div>
</template>

<script>
export default {
  name: "TopDatasetSettingsFeedbackTask",
  props: {
    separator: {
      type: Boolean,
      default: true,
    },
  },
};
</script>

<style lang="scss" scoped>
.top-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 2em;
  &.--separator {
    padding-bottom: 2em;
    border-bottom: 1px solid #e6e6e6;
  }
}
</style>
