import Vue from "vue";
import { onMounted, onUnmounted, ref, watch } from "vue-demi";
import { Highlighting, LoadedSpan, Position } from "./components/highlighting";
import EntityComponent from "./components/EntityComponent.vue";
import { Entity, Span } from "./components/span-selection";
import { Question } from "~/v1/domain/entities/question/Question";
import { SpanQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { SpanAnswer } from "~/v1/domain/entities/IAnswer";

export const useSpanAnnotationTextFieldViewModel = ({
  spanQuestion,
  name,
}: {
  spanQuestion: Question;
  name: string;
}) => {
  const spanAnnotationSupported = ref(true);
  const answer = spanQuestion.answer as SpanQuestionAnswer;

  const selectEntity = (entity: Entity) => {
    answer.options.forEach((e) => {
      e.isSelected = e.id === entity?.id;
    });

    highlighting.value.changeSelectedEntity(entity);
  };

  const entityComponentFactory = (
    entityId: string,
    entityPosition: Position,
    removeSpan: () => void,
    replaceEntity: (entity: Entity) => void
  ) => {
    const entity = answer.options.find((e) => e.id === entityId);
    const EntityComponentReference = Vue.extend(EntityComponent);

    const instance = new EntityComponentReference({
      propsData: {
        entity,
        spanQuestion,
        entityPosition,
      },
    });

    instance.$on("on-remove-option", removeSpan);
    instance.$on("on-replace-option", (newEntity: Entity) => {
      selectEntity(newEntity);

      replaceEntity(newEntity);
    });

    instance.$mount();

    return instance.$el;
  };

  const updateSelectedEntity = () => {
    const selected = answer.options.find((e) => e.isSelected);

    selectEntity(selected);
  };

  const convertSpansToResponse = (spans: Span[]): SpanAnswer[] => {
    return spans
      .map((s) => {
        const option = answer.options.find((e) => e.id === s.entity.id);

        if (!option) return undefined;

        return {
          start: s.from,
          end: s.to,
          label: option.value,
        };
      })
      .filter(Boolean);
  };

  const convertResponseToSpans = (response: SpanAnswer[]): LoadedSpan[] => {
    return response
      .map((v) => {
        const option = answer.options.find((e) => e.value === v.label);

        if (!option) return undefined;

        return {
          entity: {
            id: option.id,
          },
          from: v.start,
          to: v.end,
        };
      })
      .filter(Boolean);
  };

  const highlighting = ref<Highlighting>(
    new Highlighting(name, entityComponentFactory)
  );

  watch(
    () => answer.options,
    () => {
      updateSelectedEntity();
    },
    { deep: true }
  );

  watch(
    () => highlighting.value.spans,
    (spans) => {
      const response = convertSpansToResponse(spans);

      spanQuestion.response({
        value: response,
      });
    }
  );

  onMounted(() => {
    const spans = convertResponseToSpans(spanQuestion.answer.valuesAnswered);

    try {
      highlighting.value.mount(spans);
    } catch {
      spanAnnotationSupported.value = false;
    }
  });

  onUnmounted(() => {
    highlighting.value.unmount();
  });

  return {
    spanAnnotationSupported,
    highlighting,
  };
};
