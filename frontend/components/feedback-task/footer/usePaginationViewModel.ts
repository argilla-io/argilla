import { computed } from "vue-demi";
import { usePaginationShortcuts } from "./usePaginationShortcuts";

export const usePaginationViewModel = (props, { emit }) => {
  const isFirstPage = computed(() => {
    return props.currentPage === 1;
  });

  const onClickPrev = () => {
    emit("on-click-prev");
  };
  const onClickNext = () => {
    emit("on-click-next");
  };

  const { prevButton, nextButton } = usePaginationShortcuts();

  return { isFirstPage, onClickPrev, onClickNext, prevButton, nextButton };
};
