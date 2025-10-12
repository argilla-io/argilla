import { ref, computed } from "vue-demi";
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
    // TODO: Enable editing mode for selected annotation
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
    selectTool,
    onLabelSelected,
    onFocus,
    getAnnotationColor,
    hoverAnnotation,
    unhoverAnnotation,
    selectAnnotation,
    deleteAnnotation,
  };
};
