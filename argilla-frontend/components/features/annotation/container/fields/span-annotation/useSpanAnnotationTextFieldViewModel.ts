import Vue from "vue";
import { onMounted, onUnmounted, ref, watch } from "vue-demi";
import { useSearchTextHighlight } from "../useSearchTextHighlight";
import { Highlighting, LoadedSpan, Position } from "./components/highlighting";
import EntityComponent from "./components/EntityComponent.vue";
import { Entity, Span } from "./components/span-selection";
import { Question } from "~/v1/domain/entities/question/Question";
import { SpanQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { SpanAnswer } from "~/v1/domain/entities/IAnswer";

export const useSpanAnnotationTextFieldViewModel = (props: {
  name: string;
  spanQuestion: Question;
  id: string;
  searchText: string;
}) => {
  const { name, spanQuestion, id } = props;
  const searchTextHighlight = useSearchTextHighlight(name);
  const spanAnnotationSupported = ref(true);
  const answer = spanQuestion.answer as SpanQuestionAnswer;
  const initialConfiguration = {
    allowOverlap: spanQuestion.settings.allow_overlapping,
  };

  const selectEntity = (entity: Entity) => {
    answer.options.forEach((e) => {
      e.isSelected = e.id === entity?.id;
    });

    highlighting.value.changeSelectedEntity(entity);
  };

  const entityComponentFactory = (
    span: Span,
    entityPosition: Position,
    hoverSpan: (isHovered: boolean) => void,
    removeSpan: (span: Span) => void,
    replaceEntity: (entity: Entity) => void,
    cloneSpanWith: (span: Span, entity: Entity) => void
  ) => {
    const EntityComponentReference = Vue.extend(EntityComponent);
    const entity = answer.options.find((e) => e.id === span.entity.id);
    const suggestion = spanQuestion.suggestion?.getSuggestion({
      start: span.from,
      end: span.to,
      label: entity?.value,
    });

    const spanInRange = highlighting.value.spans.filter(
      (entity) => entity.from === span.from && entity.to === span.to
    );

    const instance = new EntityComponentReference({
      propsData: {
        span,
        spanInRange,
        entity,
        spanQuestion,
        entityPosition,
        suggestion,
      },
    });

    instance.$on("on-remove-span", removeSpan);
    instance.$on("on-hover-span", hoverSpan);
    instance.$on("on-add-span-base-on", cloneSpanWith);
    instance.$on("on-replace-entity", (newEntity: Entity) => {
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
    new Highlighting(id, entityComponentFactory, initialConfiguration)
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
      const nodeSpans = spans.filter((s) => s.node.id === id);

      const response = convertSpansToResponse(nodeSpans);

      spanQuestion.answer.response({ value: response });
    },
    {
      deep: true,
    }
  );

  watch(
    () => props.searchText,
    (newValue) => {
      searchTextHighlight.highlightText(newValue);
    }
  );

  onMounted(() => {
    const spans = convertResponseToSpans(spanQuestion.answer.valuesAnswered);

    try {
      highlighting.value.mount(spans);
    } catch {
      spanAnnotationSupported.value = false;
    }

    searchTextHighlight.highlightText(props.searchText);
  });

  onUnmounted(() => {
    highlighting.value.unmount();
  });

  return {
    spanAnnotationSupported,
    highlighting,
  };
};
