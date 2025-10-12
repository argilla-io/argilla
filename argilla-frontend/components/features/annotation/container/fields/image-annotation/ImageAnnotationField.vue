<template>
  <div class="image-annotation-field" :key="content">
    <span class="image-annotation-field__title" v-text="title" />
    <div class="image-annotation-field__canvas-wrapper">
      <div v-if="!imageLoaded && !hasError" class="image-annotation-field__loading">
        <BaseSpinner />
      </div>
      <div v-if="hasError" class="image-annotation-field__error">
        <img src="images/img-placeholder.svg" />
        <p v-text="$t('couldNotLoadImage')" />
      </div>
      <div ref="canvasContainer" class="image-annotation-field__canvas"></div>
      
      <!-- Context Menu -->
      <div
        v-if="contextMenu.visible"
        class="image-annotation-field__context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
        @click.stop="handleContextMenuDelete"
      >
        <div class="context-menu-item">
          <span>Delete Annotation</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useImageAnnotationFieldViewModel } from "./useImageAnnotationFieldViewModel";

export default {
  props: {
    id: {
      type: String,
      required: true,
    },
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
    imageAnnotationQuestion: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    return useImageAnnotationFieldViewModel(props);
  },
};
</script>

<style lang="scss" scoped>
.image-annotation-field {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  min-width: 100%;
  gap: $base-space * 2;
  padding: 2 * $base-space;
  background: var(--bg-field);
  border-radius: $border-radius-m;
  border: 1px solid var(--border-field);

  &__title {
    word-break: break-word;
    width: calc(100% - 30px);
    color: var(--fg-secondary);
  }

  &__canvas-wrapper {
    position: relative;
    width: 100%;
    height: 100%;
    overflow-y: hidden;
    overflow-x: scroll;
    text-align: center;
    min-height: 400px;
  }

  &__canvas {
    width: 100%;
    height: 100%;
  }

  &__loading,
  &__error {
    display: flex;
    flex-direction: column;
    width: 300px;
    max-width: 100%;
    margin: auto;
    align-items: center;
    justify-content: center;
    color: var(--bg-opacity-37);
  }

  &__context-menu {
    position: fixed;
    background-color: hsl(214.3, 9.6%, 14.3%);
    border: 1px solid var(--border-field);
    border-radius: $border-radius-s;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    min-width: 160px;
    padding: calc($base-space / 2);

    .context-menu-item {
      padding: $base-space;
      cursor: pointer;
      border-radius: $border-radius-s;
      color: var(--fg-primary);
      @include font-size(14px);
      transition: background 0.2s;

      &:hover {
        background: var(--bg-opacity-16);
        color: var(--fg-error);
      }
    }
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