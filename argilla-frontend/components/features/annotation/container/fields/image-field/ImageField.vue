<template>
  <div class="image_field" :key="content">
    <span class="image_field_title" v-text="title" />
    <div class="image_field__wrapper" v-if="!hasError">
      <BaseSpinner v-if="!isLoaded" />
      <img
        v-show="isLoaded"
        :src="content"
        @error="handleError()"
        @load="onLoad()"
      />
    </div>
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
  gap: $base-space * 2;
  padding: 2 * $base-space;
  background: var(--bg-field);
  border-radius: $border-radius-m;
  border: 1px solid var(--border-field);

  &_placeholder {
    display: flex;
    flex-direction: column;
    width: 300px;
    max-width: 100%;
    margin: auto;
    align-items: center;
    color: var(--bg-opacity-37);
  }

  &__wrapper {
    width: 100%;
    height: 100%;
    overflow-y: hidden;
    overflow-x: scroll;
    text-align: center;
    img {
      max-width: 100%;
    }
  }

  &_title {
    word-break: break-word;
    width: calc(100% - 30px);
    color: var(--fg-secondary);
  }
}
::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 4px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  border-radius: $base-space;
  background-color: var(--bg-opacity-54);
  box-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}
</style>
