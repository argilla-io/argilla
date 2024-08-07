<template>
  <div class="image_field" :key="content">
    <span class="image_field_title" v-text="title" />
    <img v-if="!hasError" :src="content" @error="handleError()" />
    <div v-else class="image_field_placeholder">
      <img src="images/img-placeholder.svg" />
      <p v-text="$t('couldNotLoadImage')" />
    </div>
  </div>
</template>

<script>
export default {
  props: {
    name: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    content: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      hasError: false,
    };
  },
  methods: {
    handleError() {
      this.hasError = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.image_field {
  $this: &;
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: $base-space * 2;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;

  &_placeholder {
    display: flex;
    flex-direction: column;
    width: 100%;
    align-items: center;
    color: $black-37;
  }

  img {
    width: 70%;
  }

  &_title {
    word-break: break-word;
    width: calc(100% - 30px);
  }
}
</style>
