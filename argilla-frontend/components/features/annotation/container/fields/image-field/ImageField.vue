<template>
  <div class="image_field" :key="content">
    <span class="image_field_title" v-text="title" />
    <template v-if="!hasError">
      <BaseSpinner v-if="!isLoaded" />
      <img
        v-show="isLoaded"
        :src="content"
        @error="handleError()"
        @load="onLoad()"
      />
    </template>
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
      isLoaded: false,
    };
  },
  methods: {
    handleError() {
      this.hasError = true;
    },
    onLoad() {
      this.isLoaded = true;
    },
  },
};
</script>

<style lang="scss" scoped>
.image_field {
  $this: &;
  display: flex;
  flex-direction: column;
  min-height: 100%;
  min-width: 100%;
  height: fit-content;
  width: fit-content;
  gap: $base-space * 2;
  padding: 2 * $base-space;
  background: palette(grey, 800);
  border-radius: $border-radius-m;

  &_placeholder {
    display: flex;
    flex-direction: column;
    width: 300px;
    max-width: 100%;
    margin: auto;
    align-items: center;
    color: var(--bg-opacity-37);
  }

  img {
    max-width: fit-content;
    max-height: fit-content;
    height: fit-content;
    width: fit-content;
  }

  &_title {
    word-break: break-word;
    width: calc(100% - 30px);
  }
}
</style>
