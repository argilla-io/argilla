import { DomainEvents } from "@codescouts/events";
import { onMounted, onUnmounted } from "vue-demi";

export const useEvents = (creator: Function) => {
  onMounted(() => {
    creator();
  });
  onUnmounted(() => {
    DomainEvents.clear();
  });
};
