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
              :key="`annotation-${index}-${annotation.label}`"
              class="annotation-group"
              @click="onAnnotationItemClick(index)"
            >
              <!-- Parent Annotation -->
              <div
                class="annotation-item"
                :class="{ 'annotation-item--hovered': hoveredAnnotation === index }"
                @mouseenter="hoverAnnotation(index)"
                @mouseleave="unhoverAnnotation()"
              >
                <!-- Expand/Collapse Button (only if has holes) -->
                <button
                  v-if="annotation.holes && annotation.holes.length > 0"
                  class="annotation-expand"
                  @click.stop="toggleExpanded(index)"
                  :title="isExpanded(index) ? $t('imageAnnotation.buttons.collapse') : $t('imageAnnotation.buttons.expand')"
                >
                  <span class="expand-icon">{{ isExpanded(index) ? '▼' : '▶' }}</span>
                </button>
                <span v-else class="annotation-expand-spacer" />
                
                <span
                  class="annotation-color"
                  :style="{ backgroundColor: getAnnotationColor(annotation.label) }"
                />
                <span class="annotation-label">{{ annotation.label }}</span>
                <span class="annotation-type">{{ annotation.shape_type }}</span>
                
                <!-- Hole Count Badge -->
                <span
                  v-if="annotation.holes && annotation.holes.length > 0"
                  class="annotation-hole-badge"
                  :title="$tc('imageAnnotation.tooltips.holesCount', annotation.holes.length, { count: annotation.holes.length })"
                >
                  <span class="hole-icon">⬚</span>
                  {{ annotation.holes.length }}
                </span>
                
                <div class="annotation-actions">
                  <!-- Add Hole Button -->
                  <button
                    v-if="!annotation.holes || annotation.holes.length < 10"
                    class="annotation-add-hole"
                    @click.stop="onAddHole(index)"
                    :title="$t('imageAnnotation.buttons.addHole')"
                  >
                    <span class="add-hole-icon">⬚</span>
                  </button>
                  
                  <button
                    class="annotation-edit"
                    @click.stop="onEditAnnotation(index)"
                    :title="$t('imageAnnotation.buttons.edit')"
                  >
                    <svgicon 
                      name="pen" 
                      width="12" 
                      height="12" 
                      aria-hidden="true"
                    />
                  </button>
                  <button
                    class="annotation-delete"
                    @click.stop="deleteAnnotation(index)"
                    :title="$t('imageAnnotation.buttons.delete')"
                  >
                    <svgicon 
                      name="close" 
                      width="12" 
                      height="12" 
                      aria-hidden="true"
                    />
                  </button>
                </div>
              </div>
              
              <!-- Holes List (expandable) -->
              <div
                v-if="annotation.holes && annotation.holes.length > 0"
                v-show="isExpanded(index)"
                class="holes-list"
              >
                <div
                  v-for="(hole, holeIndex) in annotation.holes"
                  :key="`${index}-hole-${holeIndex}`"
                  class="hole-item"
                >
                  <span class="hole-indent" />
                  <span class="hole-icon-small">⬚</span>
                  <span class="hole-label">Hole {{ holeIndex + 1 }}</span>
                  <span class="hole-type">{{ hole.shape_type }}</span>
                  <div class="hole-actions">
                    <button
                      class="hole-delete"
                      @click.stop="deleteHole(index, holeIndex)"
                      :title="$t('imageAnnotation.buttons.deleteHole')"
                    >
                      <svgicon 
                        name="close" 
                        width="10" 
                        height="10" 
                        aria-hidden="true"
                      />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useImageAnnotationQuestionViewModel } from "./useImageAnnotationQuestionViewModel";
import "assets/icons/close";
import "assets/icons/pen";

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
    
    // Select first label by default if none selected
    const answer = props.question.answer;
    const hasSelectedLabel = answer.options.some(opt => opt.isSelected);
    if (!hasSelectedLabel && answer.options.length > 0) {
      answer.options[0].isSelected = true;
    }
    
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
  gap: $base-space * 0.5;
}

.annotation-group {
  display: flex;
  flex-direction: column;
}

.annotation-item {
  display: flex;
  align-items: center;
  gap: $base-space;
  padding: $base-space;
  border-radius: $border-radius-s;
  cursor: pointer;
  transition: background-color 0.15s ease-out;
  will-change: background-color;

  &:hover {
    background: var(--bg-opacity-16);
  }

  &--hovered {
    background: var(--bg-opacity-24);
  }
}

.annotation-expand {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: var(--fg-secondary);
  transition: color 0.2s;

  &:hover {
    color: var(--fg-primary);
  }
}

.expand-icon {
  font-size: 10px;
  line-height: 1;
}

.annotation-expand-spacer {
  width: 16px;
  flex-shrink: 0;
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

.annotation-hole-badge {
  display: flex;
  align-items: center;
  gap: $base-space * 0.25;
  padding: $base-space * 0.25 $base-space * 0.5;
  background: var(--bg-opacity-16);
  border-radius: $border-radius-s;
  color: var(--fg-secondary);
  @include font-size(11px);
  font-weight: 600;
  flex-shrink: 0;
}

.hole-icon {
  font-size: 12px;
  line-height: 1;
  color: var(--bg-brand);
}

.annotation-actions {
  display: flex;
  gap: $base-space * 0.5;
  align-items: center;
}

.annotation-add-hole {
  background: none;
  border: 1px solid var(--border-field);
  cursor: pointer;
  padding: $base-space * 0.5;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
  color: var(--fg-secondary);

  &:hover {
    background-color: var(--bg-opacity-8);
    border-color: var(--bg-brand);
    color: var(--bg-brand);
  }
}

.add-hole-icon {
  font-size: 14px;
  line-height: 1;
}

.annotation-edit,
.annotation-delete {
  background: none;
  border: none;
  cursor: pointer;
  padding: $base-space * 0.5;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s ease;

  :deep(svg) {
    fill: var(--fg-secondary);
  }

  &:hover {
    background-color: var(--bg-opacity-1);
    
    :deep(svg) {
      fill: var(--fg-primary);
    }
  }
}

.annotation-delete {
  &:hover :deep(svg) {
    fill: var(--fg-error);
  }
}

// Holes List
.holes-list {
  display: flex;
  flex-direction: column;
  gap: $base-space * 0.25;
  padding-left: $base-space * 2;
  margin-top: $base-space * 0.25;
  will-change: opacity;
  transition: opacity 0.15s ease-out;
}

.hole-item {
  display: flex;
  align-items: center;
  gap: $base-space * 0.5;
  padding: $base-space * 0.5 $base-space;
  border-radius: $border-radius-s;
  background: var(--bg-opacity-4);
  transition: background-color 0.15s ease-out;
  will-change: background-color;

  &:hover {
    background: var(--bg-opacity-12);
  }
}

.hole-indent {
  width: 2px;
  height: 16px;
  background: var(--border-field);
  flex-shrink: 0;
  border-radius: 1px;
}

.hole-icon-small {
  font-size: 12px;
  line-height: 1;
  color: var(--fg-secondary);
  flex-shrink: 0;
}

.hole-label {
  flex: 1;
  color: var(--fg-secondary);
  @include font-size(13px);
}

.hole-type {
  color: var(--fg-tertiary);
  @include font-size(11px);
  text-transform: capitalize;
}

.hole-actions {
  display: flex;
  gap: $base-space * 0.25;
  align-items: center;
}

.hole-delete {
  background: none;
  border: none;
  cursor: pointer;
  padding: $base-space * 0.25;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s ease;

  :deep(svg) {
    fill: var(--fg-tertiary);
  }

  &:hover {
    background-color: var(--bg-opacity-8);
    
    :deep(svg) {
      fill: var(--fg-error);
    }
  }
}
</style>
