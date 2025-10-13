import { ref, type Ref } from "vue-demi";
import { ImageAnnotationQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";

export type ImageAnnotationSharedState = {
  editModeActive: Ref<boolean>;
  currentAnnotationIndex: Ref<number | null>;
  // Counter-based signals - increment to trigger action
  cancelPolygonTrigger: Ref<number>;
  reassignLabelTrigger: Ref<number>;
  reassignLabelData: Ref<{ labelValue: string } | null>;
  deleteShapeTrigger: Ref<number>;
  deleteShapeData: Ref<{ index: number } | null>;
  deleteHoleTrigger: Ref<number>;
  deleteHoleData: Ref<{ annotationIndex: number; holeIndex: number } | null>;
  enterEditModeTrigger: Ref<number>;
  enterEditModeData: Ref<{ index: number } | null>;
  exitEditModeTrigger: Ref<number>;
  selectLabelTrigger: Ref<number>;
  selectLabelData: Ref<{ labelValue: string } | null>;
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
      // Counter-based signals
      cancelPolygonTrigger: ref(0),
      reassignLabelTrigger: ref(0),
      reassignLabelData: ref(null),
      deleteShapeTrigger: ref(0),
      deleteShapeData: ref(null),
      deleteHoleTrigger: ref(0),
      deleteHoleData: ref(null),
      enterEditModeTrigger: ref(0),
      enterEditModeData: ref(null),
      exitEditModeTrigger: ref(0),
      selectLabelTrigger: ref(0),
      selectLabelData: ref(null),
      holeDrawingMode: ref({ active: false, parentIndex: null }),
    };
    
    sharedStateMap.set(answer, state);
  }
  
  return state;
};
