import { ref } from "vue-demi";
import Konva from "konva";

export interface ContextMenuState {
  visible: boolean;
  x: number;
  y: number;
  annotationIndex: number | null;
  holeIndex: number | null;
}

export interface ContextMenuActions {
  onDelete: (annotationIndex: number) => void;
  onEdit: (annotationIndex: number) => void;
  onAddHole: (annotationIndex: number) => void;
  onDeleteHole: (annotationIndex: number, holeIndex: number) => void;
}

/**
 * Consolidated context menu composable
 * Manages state, visibility, and action handlers for annotation context menus
 *
 * @param actions - Callbacks for menu actions (delete, edit, add hole, delete hole)
 * @returns Context menu state and handler functions
 */
export const useContextMenu = (actions?: ContextMenuActions) => {
  const state = ref<ContextMenuState>({
    visible: false,
    x: 0,
    y: 0,
    annotationIndex: null,
    holeIndex: null,
  });

  /**
   * Show context menu at specified position
   */
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

  /**
   * Hide context menu and reset state
   */
  const hide = () => {
    state.value = {
      visible: false,
      x: 0,
      y: 0,
      annotationIndex: null,
      holeIndex: null,
    };
  };

  /**
   * Handle delete action from context menu
   */
  const handleDelete = () => {
    if (state.value.annotationIndex !== null && actions) {
      actions.onDelete(state.value.annotationIndex);
      hide();
    }
  };

  /**
   * Handle edit action from context menu
   */
  const handleEdit = () => {
    if (state.value.annotationIndex !== null && actions) {
      actions.onEdit(state.value.annotationIndex);
    }
  };

  /**
   * Handle add hole action from context menu
   */
  const handleAddHole = () => {
    if (state.value.annotationIndex !== null && actions) {
      actions.onAddHole(state.value.annotationIndex);
      hide();
    }
  };

  /**
   * Handle delete hole action from context menu
   */
  const handleDeleteHole = () => {
    if (
      state.value.annotationIndex !== null &&
      state.value.holeIndex !== null &&
      actions
    ) {
      actions.onDeleteHole(state.value.annotationIndex, state.value.holeIndex);
      hide();
    }
  };

  /**
   * Attach context menu handler to a Konva element
   * This creates the right-click behavior for annotations
   */
  const attachContextMenuHandler = (
    element: Konva.Node,
    annotationIndex: number,
    holeIndex?: number
  ) => {
    element.on("contextmenu", (e) => {
      e.evt.preventDefault();

      if (holeIndex !== undefined) {
        e.cancelBubble = true; // Prevent parent group from handling
      }

      const stage = element.getStage();
      if (stage) {
        const pointerPos = stage.getPointerPosition();
        if (pointerPos) {
          const container = stage.container();
          const rect = container.getBoundingClientRect();
          show(
            annotationIndex,
            rect.left + pointerPos.x,
            rect.top + pointerPos.y,
            holeIndex
          );
        }
      }
    });
  };

  return {
    state,
    show,
    hide,
    handleDelete,
    handleEdit,
    handleAddHole,
    handleDeleteHole,
    attachContextMenuHandler,
  };
};
