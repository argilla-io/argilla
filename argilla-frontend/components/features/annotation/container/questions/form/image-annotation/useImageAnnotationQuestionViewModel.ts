import { ref, computed, watch, type Ref } from "vue-demi";
import { Question } from "~/v1/domain/entities/question/Question";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";

type Tool = "rectangle" | "polygon";

export const useImageAnnotationQuestionViewModel = (props: {
  question: Question;
}) => {
  const { question } = props;
  
  const selectedTool = ref<Tool>("rectangle");
  const hoveredAnnotation = ref<number | null>(null);

  const answer = question.answer as ImageAnnotationQuestionAnswer;

  type SharedState = {
    editModeActive: Ref<boolean>;
    currentAnnotationIndex: Ref<number | null>;
    reassignLabel: Ref<{ labelValue: string; timestamp: number } | null>;
  };

  const ensureSharedState = (target: ImageAnnotationQuestionAnswer): SharedState => {
    const answerTarget = target as any;
    if (!answerTarget.__imageAnnotationSync) {
      const syncState: SharedState = {
        editModeActive: ref(false),
        currentAnnotationIndex: ref<number | null>(null),
        reassignLabel: ref(null),
      };
      answerTarget.__imageAnnotationSync = syncState;
    }
    return answerTarget.__imageAnnotationSync as SharedState;
  };

  const sharedState = ensureSharedState(answer);
  const editModeActive = sharedState.editModeActive;

  watch(sharedState.editModeActive, (state) => {
    if (state) {
      // keep local state aligned when external edit mode starts
      sharedState.currentAnnotationIndex.value ??= 0;
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
    // Signal to field component to enter edit mode
    (answer as any).enterEditMode = index;
    sharedState.editModeActive.value = true;
    sharedState.currentAnnotationIndex.value = index;
    
    // Reset flag after a tick
    setTimeout(() => {
      (answer as any).enterEditMode = null;
    }, 100);
  };

  const toggleEditMode = () => {
    if (editModeActive.value) {
      // Exit edit mode
      (answer as any).exitEditMode = true;
      editModeActive.value = false;
      
      setTimeout(() => {
        (answer as any).exitEditMode = false;
      }, 100);
    } else {
      // Enter edit mode with first annotation
      if (annotations.value.length > 0) {
        onEditAnnotation(0);
      }
    }
  };

  const deleteAnnotation = (index: number) => {
    answer.values.splice(index, 1);
    updateAnswer();
  };

  const updateAnswer = () => {
    question.answer.response({
      value: answer.valuesAnswered,
    });
  };

  return {
    selectedTool,
    hoveredAnnotation,
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
    toggleEditMode,
  };
};
