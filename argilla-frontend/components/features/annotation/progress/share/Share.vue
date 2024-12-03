<template>
  <div class="share">
    <BaseButton
      class="primary"
      @mouseover="openDialog"
      @mouseleave="closeDialog"
      @click.stop="copyOnClipboard"
    >
      Share your progress
    </BaseButton>
    <transition name="fade" appear>
      <dialog
        v-if="isDialogOpen"
        class="share__dialog"
        v-click-outside="closeDialog"
      >
        <img :src="imageLink" />
      </dialog>
    </transition>
  </div>
</template>
<script>
export default {
  data() {
    return {
      isDialogOpen: false,
    };
  },
  computed: {
    imageLink() {
      return "https://assets.imglab-cdn.net/man.jpeg?width=1280&height=720&mode=crop&crop=left&text=RENDER+DYNAMIC+TEXT+TO+%3Cspan+bgcolor%3D%27yellow%27%3EIMPACT+YOUR+AUDIENCE.%3C%2Fspan%3E&text-font=Neutral+Face&text-width=640&text-height=720&text-position=left%2Cmiddle&text-weight=900&text-padding=30&text-padding-top=40&text-line-height=1.05&text-color=0%2C0%2C0%2C240&strip=all&format=webp&signature=Lggw5MwATbTH7a_fFfoW7UOjIuHAzK6Mhj9dafmuB9Y";
    },
  },
  methods: {
    copyOnClipboard() {
      this.closeDialog();

      this.$copyToClipboard(this.imageLink);

      this.$notification.notify({
        message: "Copied to clipboard",
        type: "success",
      });
    },
    openDialog() {
      this.isDialogOpen = true;
    },
    closeDialog() {
      this.isDialogOpen = false;
    },
  },
};
</script>

<style lang="scss" scoped>
.share {
  z-index: 2;
  margin-left: auto;
  margin-right: 0;

  &__dialog {
    position: absolute;
    right: 1em;
    left: auto;
    width: auto;
    min-width: 360px;
    bottom: calc(100% + $base-space + 2px);
    display: block;
    padding: $base-space * 2;
    border: 1px solid var(--bg-opacity-10);
    border-radius: $border-radius-m;
    box-shadow: $shadow;
    z-index: 2;
  }
}
</style>
