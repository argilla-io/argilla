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

  watch(
    () => answer.options,
    () => {
      const selected = answer.options.find((e) => e.isSelected);

      selectEntity(selected);
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
    selectEntity(answer.options[0]);

    const spansToLoad = answer.valuesAnswered.map((v) => ({
      entity: answer.options.find((e) => e.value === v.label),
      from: v.start,
      to: v.end,
    }));

    highlighting.value.mount(spansToLoad);
  });

  onUnmounted(() => {
    highlighting.value.unmount();
  });

  return {
    highlighting,
  };
};
