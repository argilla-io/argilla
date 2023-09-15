import { ref, Ref } from "vue-demi";

type TQuestionsFormState = {
  isQuestionsFormTouched: boolean;
  setIsQuestionsFormTouched: Function;
};
export const questionsFormState: Ref<TQuestionsFormState> = ref({
  isQuestionsFormTouched: false,

  setIsQuestionsFormTouched(value: boolean) {
    this.isQuestionsFormTouched = value;
  },
});
