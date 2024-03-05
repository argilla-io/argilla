import { watch, ref } from "vue-demi";

const getQuestionSetting = (id: string) => {
  if (!window.questionSettings) {
    window.questionSettings = {};
  }

  if (!window.questionSettings[id]) {
    window.questionSettings[id] = {
      isExpandedLabelQuestions: false,
    };
  }

  return window.questionSettings[id].isExpandedLabelQuestions;
};

const setQuestionSetting = (id: string, value: unknown) => {
  window.questionSettings[id].isExpandedLabelQuestions = value;
};

export const useLabelSelectionViewModel = ({
  componentId,
}: {
  componentId: string;
}) => {
  const isExpanded = ref(getQuestionSetting(componentId));

  watch(isExpanded, (value) => {
    setQuestionSetting(componentId, value);
  });

  return {
    isExpanded,
  };
};
