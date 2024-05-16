import { onMounted, watch } from "vue-demi";
import { useSearchTextHighlight } from "../useSearchTextHighlight";

export const useTextFieldViewModel = (props: { searchText: string }) => {
  const { highlightText } = useSearchTextHighlight();

  watch(
    () => props.searchText,
    (newValue) => {
      const fieldContent = document.getElementById("fields-content");

      highlightText(fieldContent, newValue);
    }
  );

  onMounted(() => {
    const fieldContent = document.getElementById("fields-content");

    highlightText(fieldContent, props.searchText);
  });
};
