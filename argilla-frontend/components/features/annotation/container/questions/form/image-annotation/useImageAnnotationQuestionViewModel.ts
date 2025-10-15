import { ref, computed, watch } from "vue-demi";
import { useImageAnnotationSharedState } from "../../../fields/image-annotation/useImageAnnotationSharedState";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";

type Tool = "rectangle" | "polygon";

export const useImageAnnotationQuestionViewModel = (props: {
  question: Question;
}) => {
  const { question } = props;

  const hoveredAnnotation = ref<number | null>(null);
  const expandedAnnotations = ref<Record<number, boolean>>({});

  const answer = question.answer as ImageAnnotationQuestionAnswer;

  const sharedState = useImageAnnotationSharedState(answer);
  const editModeActive = sharedState.editModeActive;
  const selectedTool = computed({
    get: () => sharedState.selectedTool.value as Tool,
    set: (value: Tool) => {
      sharedState.selectedTool.value = value;
    },
  });

  watch(sharedState.editModeActive, (state) => {
    if (state) {
      // keep local state aligned when external edit mode starts
      sharedState.currentAnnotationIndex.value ??= 0;
    }
  });

  // Watch for label selection signal from field component
  watch(sharedState.selectLabelTrigger, () => {
    const selectData = sharedState.selectLabelData.value;
    if (selectData && selectData.labelValue) {
      // Find the option with this label value
      const option = answer.options.find(
        (opt) => opt.value === selectData.labelValue
      );
      if (option) {
        // Deselect all options
        answer.options.forEach((opt) => (opt.isSelected = false));
        // Select the matching option
        option.isSelected = true;
      }
    }
  });

  const annotations = computed(() => answer.values);

  // Memoize annotation colors to avoid repeated function calls during rendering
  const annotationColorsCache = computed(() => {
    const cache = new Map<string, string>();
    annotations.value.forEach((annotation) => {
      if (!cache.has(annotation.label)) {
        cache.set(
          annotation.label,
          answer.getAnnotationColor(annotation.label)
        );
      }
    });
    return cache;
  });

  const getAnnotationColorMemoized = (labelValue: string) => {
    return (
      annotationColorsCache.value.get(labelValue) ||
      answer.getAnnotationColor(labelValue)
    );
  };

  const selectTool = (tool: Tool) => {
    // Signal to field component to cancel any ongoing polygon drawing
    if (selectedTool.value === "polygon" && tool !== "polygon") {
      sharedState.cancelPolygonTrigger.value++;
    }

    selectedTool.value = tool;
  };

  // Called when a label is selected via EntityLabelSelection component
  const onLabelSelected = () => {
    // If in edit mode, reassign the current annotation to the new label
    if (editModeActive.value) {
      // Find the currently selected label
      const selectedOption = answer.options.find((opt) => opt.isSelected);

      if (selectedOption) {
        // Set data and increment trigger - watcher will react immediately
        sharedState.reassignLabelData.value = {
          labelValue: selectedOption.value,
        };
        sharedState.reassignLabelTrigger.value++;
      } else {
        sharedState.reassignLabelData.value = null;
      }
    }
  };

  const onFocus = () => {
    // Handle focus events if needed
  };

  const hoverAnnotation = (index: number) => {
    hoveredAnnotation.value = index;
    // Note: Canvas hover highlighting is handled by the field component's own hover handlers
    // attached directly to Konva shapes. List hover only updates local UI state.
  };

  const unhoverAnnotation = () => {
    hoveredAnnotation.value = null;
  };

  const onEditAnnotation = (index: number) => {
    // If already in edit mode with this annotation, do nothing
    if (
      editModeActive.value &&
      sharedState.currentAnnotationIndex.value === index
    ) {
      return;
    }

    // Signal to field component to enter edit mode via sharedState
    sharedState.enterEditModeData.value = { index };
    sharedState.editModeActive.value = true;
    sharedState.currentAnnotationIndex.value = index;
    sharedState.enterEditModeTrigger.value++;
  };

  const toggleEditMode = () => {
    if (editModeActive.value) {
      // Exit edit mode - signal to field component
      // Don't change editModeActive here - let the field component handle it
      sharedState.exitEditModeTrigger.value++;
    } else if (annotations.value.length > 0) {
      // Enter edit mode with first annotation
      onEditAnnotation(0);
    }
  };

  /**
   * Delete a shape from the question list UI.
   * This signals the Field component to handle the actual deletion.
   */
  const deleteAnnotation = (index: number) => {
    // Signal to field component to delete this shape via sharedState
    // The field component will handle:
    // 1. Exiting edit mode if needed
    // 2. Removing the shape from the array
    // 3. Re-rendering the canvas
    sharedState.deleteShapeData.value = { index };
    sharedState.deleteShapeTrigger.value++;
  };

  const toggleExpanded = (index: number) => {
    // Use Vue.set for Vue 2 reactivity
    const currentState = expandedAnnotations.value[index] || false;
    expandedAnnotations.value = {
      ...expandedAnnotations.value,
      [index]: !currentState,
    };
  };

  const isExpanded = (index: number) => {
    return expandedAnnotations.value[index] || false;
  };

  const onAnnotationItemClick = (index: number) => {
    const annotation = annotations.value[index];
    if (!annotation) return;

    if (annotation.holes && annotation.holes.length > 0) {
      toggleExpanded(index);
    }
  };

  const onAddHole = (index: number) => {
    // Signal to field component to enter hole drawing mode
    sharedState.holeDrawingMode.value = {
      active: true,
      parentIndex: index,
    };
  };

  const deleteHole = (annotationIndex: number, holeIndex: number) => {
    const annotation = annotations.value[annotationIndex];
    if (annotation?.holes?.[holeIndex]) {
      // Signal to field component to delete this hole via sharedState
      // The field component will handle:
      // 1. Removing the hole from the array
      // 2. Re-rendering the canvas
      // 3. Updating anchor points if in edit mode
      sharedState.deleteHoleData.value = {
        annotationIndex,
        holeIndex,
      };
      sharedState.deleteHoleTrigger.value++;
    }
  };

  return {
    selectedTool,
    hoveredAnnotation,
    expandedAnnotations,
    annotations,
    editModeActive,
    selectTool,
    onLabelSelected,
    onFocus,
    getAnnotationColor: getAnnotationColorMemoized,
    hoverAnnotation,
    unhoverAnnotation,
    deleteAnnotation,
    onEditAnnotation,
    onAnnotationItemClick,
    toggleEditMode,
    toggleExpanded,
    isExpanded,
    onAddHole,
    deleteHole,
  };
};
