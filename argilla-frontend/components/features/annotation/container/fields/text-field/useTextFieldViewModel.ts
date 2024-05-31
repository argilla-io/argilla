import { onMounted, watch } from "vue-demi";
import { useSearchTextHighlight } from "../useSearchTextHighlight";

export const useTextFieldViewModel = (props: {
  name: string;
  searchText: string;
}) => {
  const { highlightText } = useSearchTextHighlight(props.name);

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
