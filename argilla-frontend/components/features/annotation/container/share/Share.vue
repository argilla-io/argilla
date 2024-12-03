<template>
  <dialog v-if="isDialogVisible" v-click-outside="closeDialog">
    <BaseButton class="primary" @click="copyRewardLink">{{
      $t("share")
    }}</BaseButton>
    <div></div>
  </dialog>
</template>
<script>
export default {
  data() {
    return {
      isDialogVisible: true,
    };
  },
  methods: {
    copyRewardLink() {
      this.$notification.notify({
        message: this.$t("linkCopied"),
        type: "success",
      });
    },
    closeDialog() {
      this.isDialogVisible = false;
    },
  },
  setup() {},
};
</script>
<style lang="scss" scoped>
dialog {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 75vw;
  height: 75vh;
  display: block;
  padding: $base-space * 2;
  background: var(--bg-accent-grey-2);
  border: 1px solid var(--bg-opacity-10);
  border-radius: $border-radius-m;
  box-shadow: $shadow;
  z-index: 2;
}
</style>
