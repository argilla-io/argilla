import { useResolve } from "ts-injecty";
import { ref } from "vue-demi";
import { Record } from "~/v1/domain/entities/record/Record";
import { DiscardRecordUseCase } from "~/v1/domain/usecases/discard-record-use-case";
import { SubmitRecordUseCase } from "~/v1/domain/usecases/submit-record-use-case";
import { SaveDraftUseCase } from "~/v1/domain/usecases/save-draft-use-case";
import { useNotifications } from "~/v1/infrastructure/services/useNotifications";

export const useFocusAnnotationViewModel = () => {
  const isDraftSaving = ref(false);
  const isDiscarding = ref(false);
  const isSubmitting = ref(false);
  const discardUseCase = useResolve(DiscardRecordUseCase);
  const submitUseCase = useResolve(SubmitRecordUseCase);
  const saveDraftUseCase = useResolve(SaveDraftUseCase);
  const { notify } = useNotifications();

  const discard = async (record: Record) => {
    try {
      isDiscarding.value = true;

      await discardUseCase.execute(record);
    } catch (error) {
      notify({
        message: "Failed to discard response. Please try again.",
        type: "danger",
      });
    } finally {
      isDiscarding.value = false;
    }
  };

  const submit = async (record: Record) => {
    try {
      isSubmitting.value = true;

      await submitUseCase.execute(record);
    } catch (error) {
      // Reset image annotation states to idle mode on error
      resetImageAnnotationStates(record);

      if (error.message === "VALIDATION_ERROR") {
        notify({
          message: "Please complete all required fields correctly before submitting.",
          type: "warning",
        });
      } else if (error.response?.status === 422) {
        // Backend validation error - data format is invalid
        const detail = error.response?.data?.detail;
        let errorMessage = "Invalid data format";
        
        if (typeof detail === "string") {
          errorMessage = detail;
        } else if (detail && typeof detail === "object") {
          // Handle structured error objects (e.g., validation errors from Argilla API)
          if (detail.code && detail.params?.errors && Array.isArray(detail.params.errors)) {
            // Collect all unique error messages
            const uniqueMessages = new Set<string>();
            detail.params.errors.forEach((err: any) => {
              if (err.msg) {
                uniqueMessages.add(err.msg);
              }
            });
            
            if (uniqueMessages.size > 0) {
              // Format as an HTML list
              const messageList = Array.from(uniqueMessages)
                .map((msg) => `• ${msg}`)
                .join("<br>");
              errorMessage = `Validation errors:<br>${messageList}`;
            } else {
              // Fallback to error code
              const errorCode = detail.code.split("::").pop() || detail.code;
              errorMessage = errorCode;
            }
          } else {
            errorMessage = detail.message || detail.msg || "Invalid data format";
          }
        }
        
        notify({
          message: errorMessage,
          type: "danger",
        });
      } else {
        notify({
          message: "Failed to submit response. Please check your data and try again.",
          type: "danger",
        });
      }
      throw error; // Re-throw to prevent view transition
    } finally {
      isSubmitting.value = false;
    }
  };

  const resetImageAnnotationStates = (record: Record) => {
    // Reset all image annotation questions to idle mode
    record.questions.forEach((question) => {
      if (question.isImageAnnotationType) {
        const answer = question.answer as any;
        if (answer && typeof answer.getAnnotationColor === "function") {
          // This is an ImageAnnotationQuestionAnswer
          // Import and use the shared state to reset
          const { useImageAnnotationSharedState } = require("~/components/features/annotation/container/fields/image-annotation/useImageAnnotationSharedState");
          const sharedState = useImageAnnotationSharedState(answer);
          
          // Exit edit mode
          if (sharedState.editModeActive.value) {
            sharedState.exitEditModeTrigger.value++;
          }
          
          // Cancel any ongoing polygon drawing
          sharedState.cancelPolygonTrigger.value++;
          
          // Exit hole drawing mode
          if (sharedState.holeDrawingMode.value.active) {
            sharedState.holeDrawingMode.value = { active: false, parentIndex: null };
          }
        }
      }
    });
  };

  const saveAsDraft = async (record: Record) => {
    try {
      isDraftSaving.value = true;

      await saveDraftUseCase.execute(record);
    } catch (error) {
      notify({
        message: "Failed to save draft. Please try again.",
        type: "danger",
      });
    } finally {
      isDraftSaving.value = false;
    }
  };

  return {
    isDraftSaving,
    isDiscarding,
    isSubmitting,
    submit,
    discard,
    saveAsDraft,
  };
};
