<template>
  <div class="wrapper">
    <QuestionHeaderComponent :question="question" />
    
    <div class="image-annotation-question">
      <!-- Tool Selection -->
      <div class="image-annotation-question__tools">
        <h4 class="section-title">Drawing Tools</h4>
        <div class="tools-list">
          <button
            v-for="tool in tools"
            :key="tool.type"
            class="tool-button"
            :class="{ 
              'tool-button--active': selectedTool === tool.type,
              'tool-button--disabled': editModeActive 
            }"
            @click="selectTool(tool.type)"
            :title="tool.label"
            :disabled="editModeActive"
          >
            <span class="tool-icon">{{ tool.icon }}</span>
            <span class="tool-label">{{ tool.label }}</span>
          </button>
        </div>
      </div>

      <!-- Label Selection - Using Span Annotation Component -->
      <div class="image-annotation-question__labels">
        <h4 class="section-title">Labels</h4>
        <EntityLabelSelectionComponent
          v-model="question.answer.options"
          :componentId="question.id"
          :maxOptionsToShowBeforeCollapse="question.settings.visible_options"
          :isFocused="isFocused"
          :visibleShortcuts="true"
          @on-selected="onLabelSelected"
          @on-focus="onFocus"
        />
      </div>

      <!-- Annotations List -->
      <div class="image-annotation-question__annotations">
        <h4 class="section-title">Annotations ({{ annotations.length }})</h4>
        <div class="image-annotation-question__annotations-container">
          <div class="annotations-list">
            <div
              v-for="(annotation, index) in annotations"
              :key="index"
              class="annotation-item"
              :class="{ 'annotation-item--hovered': hoveredAnnotation === index }"
              @mouseenter="hoverAnnotation(index)"
              @mouseleave="unhoverAnnotation()"
              @click="onEditAnnotation(index)"
            >
              <span
                class="annotation-color"
                :style="{ backgroundColor: getAnnotationColor(annotation.label) }"
              />
              <span class="annotation-label">{{ annotation.label }}</span>
              <span class="annotation-type">{{ annotation.shape_type }}</span>
              <button
                class="annotation-delete"
                @click.stop="deleteAnnotation(index)"
                title="Delete"
              >
                ×
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useImageAnnotationQuestionViewModel } from "./useImageAnnotationQuestionViewModel";

export default {
  name: "ImageAnnotationComponent",
  props: {
    question: {
      type: Object,
      required: true,
    },
    isFocused: {
      type: Boolean,
      default: () => false,
    },
  },
  data() {
    return {
      tools: [
        { type: "rectangle", icon: "▭", label: "Rectangle" },
        { type: "polygon", icon: "⬡", label: "Polygon" },
      ],
    };
  },
  setup(props) {
    const viewModel = useImageAnnotationQuestionViewModel(props);
    
    // Ensure rectangle tool is selected by default
    viewModel.selectTool("rectangle");
    
    return viewModel;
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-direction: column;
  gap: $base-space * 1.5;
}

.image-annotation-question {
  display: flex;
  flex-direction: column;
  gap: $base-space * 2;

  &__tools,
  &__labels,
  &__annotations {
    display: flex;
    flex-direction: column;
    gap: $base-space * 1.5;
  }

  &__annotations-container {
    background: var(--bg-opacity-8);
    border-radius: $border-radius-s;
    max-height: 300px;
    overflow-y: auto;
  }
}

.section-title {
  font-weight: 600;
  color: var(--fg-primary);
  @include font-size(14px);
  margin: 0;
}

.tools-list {
  display: flex;
  gap: $base-space;
  flex-wrap: wrap;
}

.tool-button {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: $base-space $base-space * 2;
  background: var(--bg-opacity-8);
  border: 1px solid var(--border-field);
  border-radius: $border-radius-s;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  color: var(--fg-primary);

  &:hover:not(:disabled) {
    background: var(--bg-opacity-16);
  }

  &--active {
    background: var(--bg-brand);
    color: white;
    border-color: var(--bg-brand);
  }

  &--disabled {
    opacity: 0.4;
    cursor: not-allowed;
    filter: grayscale(100%);
  }
}

.tool-icon {
  font-size: 18px;
}

.tool-label {
  @include font-size(13px);
}

.annotations-list {
  display: flex;
  flex-direction: column;
  gap: $base-space;
}

.annotation-item {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: $base-space;
  border-radius: $border-radius-s;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: var(--bg-opacity-16);
  }

  &--hovered {
    background: var(--bg-opacity-24);
  }
}

.annotation-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.annotation-label {
  flex: 1;
  color: var(--fg-primary);
  @include font-size(14px);
}

.annotation-type {
  color: var(--fg-secondary);
  @include font-size(12px);
  text-transform: capitalize;
}

.annotation-delete {
  background: none;
  border: none;
  color: var(--fg-secondary);
  font-size: 20px;
  cursor: pointer;
  padding: 0 $base-space;
  line-height: 1;

  &:hover {
    color: var(--fg-error);
  }
}
</style>
