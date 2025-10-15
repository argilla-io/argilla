import { ref, type Ref } from "vue-demi";

export type ContextMenuState = {
  visible: boolean;
  x: number;
  y: number;
  annotationIndex: number | null;
  holeIndex: number | null;
};

export type ContextMenu = {
  state: Ref<ContextMenuState>;
  show: (
    index: number,
    x: number,
    y: number,
    holeIndex?: number | null
  ) => void;
  hide: () => void;
};

/**
 * Composable for managing context menu state.
 * Provides reactive state and methods to show/hide the context menu.
 *
 * @returns Object with state ref and show/hide methods
 */
export const useContextMenu = (): ContextMenu => {
  const state = ref<ContextMenuState>({
    visible: false,
    x: 0,
    y: 0,
    annotationIndex: null,
    holeIndex: null,
  });

  const show = (
    index: number,
    x: number,
    y: number,
    holeIndex: number | null = null
  ) => {
    state.value = {
      visible: true,
      x,
      y,
      annotationIndex: index,
      holeIndex,
    };
  };

  const hide = () => {
    state.value = {
      visible: false,
      x: 0,
      y: 0,
      annotationIndex: null,
      holeIndex: null,
    };
  };

  return {
    state,
    show,
    hide,
  };
};
