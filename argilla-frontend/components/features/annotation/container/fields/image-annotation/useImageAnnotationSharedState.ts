import { ref, type Ref } from "vue-demi";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";

export type ImageAnnotationSharedState = {
  editModeActive: Ref<boolean>;
  currentAnnotationIndex: Ref<number | null>;
  reassignLabel: Ref<{ labelValue: string; timestamp: number } | null>;
  deleteShapeSignal: Ref<{ index: number; timestamp: number } | null>;
  deleteHoleSignal: Ref<{ annotationIndex: number; holeIndex: number; timestamp: number } | null>;
  enterEditModeSignal: Ref<{ index: number; timestamp: number } | null>;
  exitEditModeSignal: Ref<boolean>;
  selectLabelSignal: Ref<{ labelValue: string; timestamp: number } | null>;
  holeDrawingMode: Ref<{ active: boolean; parentIndex: number | null }>;
};

const sharedStateMap = new WeakMap<ImageAnnotationQuestionAnswer, ImageAnnotationSharedState>();

/**
 * Get or create shared state for an ImageAnnotationQuestionAnswer instance.
 * Uses WeakMap to avoid mutating the domain object and enable automatic garbage collection.
 */
export const useImageAnnotationSharedState = (
  answer: ImageAnnotationQuestionAnswer
): ImageAnnotationSharedState => {
  let state = sharedStateMap.get(answer);
  
  if (!state) {
    state = {
      editModeActive: ref(false),
      currentAnnotationIndex: ref<number | null>(null),
      reassignLabel: ref(null),
      deleteShapeSignal: ref(null),
      deleteHoleSignal: ref(null),
      enterEditModeSignal: ref(null),
      exitEditModeSignal: ref(false),
      selectLabelSignal: ref(null),
      holeDrawingMode: ref({ active: false, parentIndex: null }),
    };
    
    sharedStateMap.set(answer, state);
  }
  
  return state;
};
