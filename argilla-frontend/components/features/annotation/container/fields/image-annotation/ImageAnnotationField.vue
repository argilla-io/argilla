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

      <!-- Navigation Bar (under canvas) -->
      <div class="image-annotation-field__edit-nav">
        <!-- Hole Drawing Mode: Show parent info and exit button -->
        <template v-if="holeDrawingMode.active">
          <span class="edit-nav-counter">
            <span class="hole-mode-icon">⬚</span>
            Drawing holes - Click ESC to exit
          </span>
          <button
            class="edit-nav-button edit-nav-button--exit"
            @click="exitHoleDrawingMode"
          >
            Exit Hole Mode
          </button>
        </template>

        <!-- Edit Mode: Full navigation -->
        <template v-else-if="editMode.active">
          <button
            class="edit-nav-button"
            @click="editPreviousAnnotation"
          >
            ← <span v-text="$t('imageAnnotation.editMode.previous')" />
          </button>
          <span class="edit-nav-counter">
            {{ $t('imageAnnotation.editMode.shapeCounter', { current: (editMode.annotationIndex ?? 0) + 1, total: imageAnnotationQuestion.answer.values.length }) }}
          </span>
          <button
            class="edit-nav-button"
            @click="editNextAnnotation"
          >
            <span v-text="$t('imageAnnotation.editMode.next')" /> →
          </button>
          <button
            class="edit-nav-button edit-nav-button--exit"
            @click="exitEditMode"
            v-text="$t('imageAnnotation.editMode.exitEditMode')"
          />
        </template>

        <!-- Non-Edit Mode: Summary and Edit button -->
        <template v-else>
          <span class="edit-nav-counter">
            {{ $t('imageAnnotation.shapesCount', { count: imageAnnotationQuestion.answer.values.length }) }}
          </span>
          <button
            class="edit-nav-button edit-nav-button--primary"
            @click="enterEditMode(0)"
            :disabled="imageAnnotationQuestion.answer.values.length === 0"
            v-text="$t('imageAnnotation.editShapes')"
          />
        </template>
      </div>

      <!-- Context Menu -->
      <div
        v-if="contextMenu.visible"
        class="image-annotation-field__context-menu"
        :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      >
        <!-- Hole-specific menu -->
        <template v-if="contextMenu.holeIndex !== null">
          <div class="context-menu-item context-menu-item--delete" @click.stop="handleContextMenuDeleteHole">
            <span v-text="$t('imageAnnotation.contextMenu.deleteHole')" />
          </div>
        </template>

        <!-- Parent annotation menu -->
        <template v-else>
          <div class="context-menu-item" @click.stop="handleContextMenuEdit">
            <span v-text="$t('imageAnnotation.contextMenu.edit')" />
          </div>
          <div class="context-menu-item" @click.stop="handleContextMenuAddHole">
            <span v-text="$t('imageAnnotation.contextMenu.addHole')" />
          </div>
          <div class="context-menu-item context-menu-item--delete" @click.stop="handleContextMenuDelete">
            <span v-text="$t('imageAnnotation.contextMenu.delete')" />
          </div>
        </template>
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
    display: flex;
    flex-direction: column;
    width: 100%;
    gap: $base-space * 1.5;
  }

  &__canvas {
    width: 100%;
    min-height: 400px;
    height: 60vh;
    max-height: 700px;
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
    .context-menu-item {
      display: flex;
      align-items: center;
      gap: $base-space;
      padding: $base-space;
      cursor: pointer;
      border-radius: $border-radius-s;
      background: var(--bg-opacity-8);
      color: var(--fg-primary);
      @include font-size(14px);
      transition: background 0.2s;

      &:hover {
        background: var(--bg-opacity-16);
      }

      &:first-child:hover {
        color: var(--bg-brand);
      }

      &--delete:hover {
        color: var(--fg-error);
      }
    }

    .context-menu-icon {
      font-size: 16px;
      line-height: 1;
    }
  }

  &__edit-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: $base-space;
    padding: $base-space 0;

    .edit-nav-button {
      padding: $base-space calc($base-space * 1.5);
      background: hsl(214.3, 9.6%, 14.3%);
      border: none;
      border-radius: $border-radius-s;
      color: var(--fg-primary);
      cursor: pointer;
      @include font-size(14px);
      transition: all 0.2s;

      &:hover:not(:disabled) {
        background: hsl(214.3, 9.6%, 18%);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      &--exit {
        background: var(--bg-brand);
        color: white;
        border: none;

        &:hover {
          opacity: 0.9;
        }
      }

      &--primary {
        background: var(--bg-brand);
        color: white;
        border: none;

        &:hover:not(:disabled) {
          opacity: 0.9;
        }
      }
    }

    .edit-nav-counter {
      padding: 0 $base-space;
      color: var(--fg-primary);
      @include font-size(14px);
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: $base-space * 0.5;
    }

    .hole-mode-icon {
      font-size: 18px;
      line-height: 1;
      color: var(--bg-brand);
    }
  }
}

::-webkit-scrollbar {
  -webkit-appearance: none;
  width: 4px;
}

::-webkit-scrollbar-thumb {
  border-radius: $base-space;
  background-color: var(--bg-opacity-54);
  box-shadow: 0 0 1px rgba(255, 255, 255, 0.5);
}
</style>