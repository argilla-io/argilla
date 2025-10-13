import { ref, computed, watch, type Ref } from "vue-demi";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { useImageAnnotationSharedState } from "../../../fields/image-annotation/useImageAnnotationSharedState";

type Tool = "rectangle" | "polygon";

export const useImageAnnotationQuestionViewModel = (props: {
  question: Question;
}) => {
  const { question } = props;
  
  const selectedTool = ref<Tool>("rectangle");
  const hoveredAnnotation = ref<number | null>(null);
  const expandedAnnotations = ref<Record<number, boolean>>({});

  const answer = question.answer as ImageAnnotationQuestionAnswer;

  const sharedState = useImageAnnotationSharedState(answer);
  const editModeActive = sharedState.editModeActive;

  watch(sharedState.editModeActive, (state) => {
    if (state) {
      // keep local state aligned when external edit mode starts
      sharedState.currentAnnotationIndex.value ??= 0;
    }
  });

  // Watch for label selection signal from field component
  watch(sharedState.selectLabelSignal, (selectData) => {
    if (selectData && selectData.labelValue) {
      // Find the option with this label value
      const option = answer.options.find(opt => opt.value === selectData.labelValue);
      if (option) {
        // Deselect all options
        answer.options.forEach(opt => opt.isSelected = false);
        // Select the matching option
        option.isSelected = true;
      }
    }
  });

  const annotations = computed(() => answer.values);

  // Initialize the selected tool in the answer object
  (answer as any).selectedTool = selectedTool.value;
  const selectTool = (tool: Tool) => {
    // Signal to field component to cancel any ongoing polygon drawing
    if (selectedTool.value === "polygon" && tool !== "polygon") {
      (answer as any).cancelPolygon = true;
      // Reset flag after a tick
      setTimeout(() => {
        (answer as any).cancelPolygon = false;
      }, 100);
    }
    
    selectedTool.value = tool;
    // Store the selected tool in the answer object for the field to access
    (answer as any).selectedTool = tool;
  };

  // Called when a label is selected via EntityLabelSelection component
  const onLabelSelected = () => {
    // The EntityLabelSelection component already handles the selection logic
    // We just need to ensure the selected tool is stored
    (answer as any).selectedTool = selectedTool.value;
    
    // If in edit mode, reassign the current annotation to the new label
    if (editModeActive.value) {
      // Find the currently selected label
      const selectedOption = answer.options.find((opt) => opt.isSelected);
      
      if (selectedOption) {
        const reassignData = {
          labelValue: selectedOption.value,
          timestamp: Date.now(),
        };

        sharedState.reassignLabel.value = reassignData;

        // Reset flag after a tick to allow consecutive reassignments
        setTimeout(() => {
          if (sharedState.reassignLabel.value?.timestamp === reassignData.timestamp) {
            sharedState.reassignLabel.value = null;
          }
        }, 0);
      } else {
        sharedState.reassignLabel.value = null;
      }
    }
  };

  const onFocus = () => {
    // Handle focus events if needed
  };

  const getAnnotationColor = (labelValue: string) => {
    const option = answer.options.find((opt) => opt.value === labelValue);
    return option?.color || "#cccccc";
  };

  const hoverAnnotation = (index: number) => {
    hoveredAnnotation.value = index;
    // TODO: Emit event to field component to highlight annotation
  };

  const unhoverAnnotation = () => {
    hoveredAnnotation.value = null;
    // TODO: Emit event to field component to unhighlight annotation
  };

  const selectAnnotation = (index: number) => {
    // Clicking on annotation in list - could trigger edit mode
  };

  const onEditAnnotation = (index: number) => {
    // If already in edit mode with this annotation, do nothing
    if (editModeActive.value && sharedState.currentAnnotationIndex.value === index) {
      return;
    }
    
    // Signal to field component to enter edit mode via sharedState
    sharedState.enterEditModeSignal.value = { index, timestamp: Date.now() };
    sharedState.editModeActive.value = true;
    sharedState.currentAnnotationIndex.value = index;
    
    // Reset flag after a tick
    setTimeout(() => {
      sharedState.enterEditModeSignal.value = null;
    }, 100);
  };

  const toggleEditMode = () => {
    if (editModeActive.value) {
      // Exit edit mode - signal to field component
      // Don't change editModeActive here - let the field component handle it
      sharedState.exitEditModeSignal.value = true;
      
      setTimeout(() => {
        sharedState.exitEditModeSignal.value = false;
      }, 100);
    } else {
      // Enter edit mode with first annotation
      if (annotations.value.length > 0) {
        onEditAnnotation(0);
      }
    }
  };

  /**
   * Delete a shape from the question list UI.
   * This signals the Field component to handle the actual deletion.
   */
  const deleteShapeFromList = (index: number) => {
    // Signal to field component to delete this shape via sharedState
    // The field component will handle:
    // 1. Exiting edit mode if needed
    // 2. Removing the shape from the array
    // 3. Re-rendering the canvas
    sharedState.deleteShapeSignal.value = { index, timestamp: Date.now() };
    
    setTimeout(() => {
      sharedState.deleteShapeSignal.value = null;
    }, 100);
  };
  
  // Keep old name for backward compatibility temporarily
  const deleteAnnotation = deleteShapeFromList;

  const toggleExpanded = (index: number) => {
    expandedAnnotations.value[index] = !expandedAnnotations.value[index];
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
    if (annotation && annotation.holes && annotation.holes[holeIndex]) {
      // Signal to field component to delete this hole via sharedState
      // The field component will handle:
      // 1. Removing the hole from the array
      // 2. Re-rendering the canvas
      // 3. Updating anchor points if in edit mode
      sharedState.deleteHoleSignal.value = { 
        annotationIndex, 
        holeIndex, 
        timestamp: Date.now() 
      };
      
      setTimeout(() => {
        sharedState.deleteHoleSignal.value = null;
      }, 100);
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
    getAnnotationColor,
    hoverAnnotation,
    unhoverAnnotation,
    selectAnnotation,
    deleteAnnotation,
    onEditAnnotation,
    onAnnotationItemClick,
    toggleEditMode,
    toggleExpanded,
    onAddHole,
    deleteHole,
  };
};
