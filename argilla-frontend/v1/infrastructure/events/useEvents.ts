import { DomainEvent, Handler } from "@codescouts/events";
import { useResolve } from "ts-injecty";
import { Ref } from "ts-injecty/dist/types";
import { onMounted, onUnmounted, ref } from "vue-demi";

export const useEvents = (...handlers: Ref<Handler<DomainEvent>>[]) => {
  const resolved = ref([]);

  onMounted(() => {
    resolved.value = handlers.map((handler) => useResolve(handler));
  });

  onUnmounted(() => {
    resolved.value.forEach((handler) => handler.dispose());
  });
};
