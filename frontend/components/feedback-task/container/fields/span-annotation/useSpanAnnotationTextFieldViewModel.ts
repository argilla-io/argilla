import Vue from "vue";
import { onMounted, onUnmounted, ref, watch } from "vue-demi";
import { Highlighting, Position } from "./components/highlighting";
import EntityComponent from "./components/EntityComponent.vue";
import { Entity } from "./components/span-selection";
import { Question } from "~/v1/domain/entities/question/Question";
import { SpanQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";
import { SpanAnswer } from "~/v1/domain/entities/IAnswer";

export const useSpanAnnotationTextFieldViewModel = ({
  spanQuestion,
  title,
}: {
  spanQuestion: Question;
  title: string;
}) => {
  const spanAnnotationSupported = ref(true);
  const answer = spanQuestion.answer as SpanQuestionAnswer;

  const selectEntity = (entity) => {
    answer.options.forEach((e) => {
      e.isSelected = e.id === entity.id;
    });

    highlighting.value.changeSelectedEntity(entity);
  };

  const entityComponentFactory = (
    entity: Entity,
    entityPosition: Position,
    removeSpan: () => void,
    replaceEntity: (entity: Entity) => void
  ) => {
    const EntityComponentReference = Vue.extend(EntityComponent);

    const instance = new EntityComponentReference({
      propsData: {
        entity,
        spanQuestion,
        entityPosition,
      },
    });

    instance.$on("on-remove-option", removeSpan);
    instance.$on("on-replace-option", (newEntity) => {
      selectEntity(newEntity);

      replaceEntity(newEntity);
    });

    instance.$mount();

    return instance.$el;
  };

  const highlighting = ref<Highlighting>(
    new Highlighting(title, answer.options, entityComponentFactory, {
      entitiesGap: 9,
    })
  );

  const updateSelectedEntity = () => {
    const selected = answer.options.find((e) => e.isSelected);

    selectEntity(selected);
  };

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
      const response: SpanAnswer[] = spans.map((s) => ({
        start: s.from,
        end: s.to,
        label: s.entity.value,
      }));

      spanQuestion.response({
        value: response,
      });
    }
  );

  onMounted(() => {
    updateSelectedEntity();

    const spansToLoad = answer.valuesAnswered.map((v) => ({
      entity: answer.options.find((e) => e.value === v.label),
      from: v.start,
      to: v.end,
    }));

    try {
      highlighting.value.mount(spansToLoad);
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
