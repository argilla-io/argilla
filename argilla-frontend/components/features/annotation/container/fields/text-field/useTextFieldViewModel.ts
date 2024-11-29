import { onMounted, watch } from "vue-demi";
import { useSearchTextHighlight } from "../useSearchTextHighlight";

export const useTextFieldViewModel = (props: {
  id: string;
  searchText: string;
}) => {
  const { highlightText } = useSearchTextHighlight(props.id);

  watch(
    () => props.searchText,
    (newValue) => {
      highlightText(newValue);
    }
  );

  onMounted(() => {
    highlightText(props.searchText);
  });
};
