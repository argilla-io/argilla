import Vue from "vue";
import { onMounted, onUnmounted, ref, watch } from "vue-demi";
import { Highlighting, Position } from "./components/highlighting";
import { colorGenerator } from "./components/color-generator";
import EntityComponent from "./components/EntityComponent.vue";
import { Entity } from "./components/span-selection";
import { Question } from "~/v1/domain/entities/question/Question";
import { SpanQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";

export const useSpanAnnotationTextFieldViewModel = ({
  spanQuestion,
  title,
}: {
  spanQuestion: Question;
  title: string;
}) => {
  const answer = spanQuestion.answer as SpanQuestionAnswer;

  answer.entities
    .filter((e) => !e.color)
    .forEach((e) => {
      e.color = colorGenerator(e.id);
    });

  const mapEntitiesForHighlighting = (e) => ({ id: e.id, text: e.name });

  const selectEntity = (entity) => {
    answer.entities.forEach((e) => {
      e.isSelected = e.id === entity.id;
    });

    highlighting.value.changeSelectedEntity(mapEntitiesForHighlighting(entity));
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

    instance.$on("on-remove-entity", removeSpan);
    instance.$on("on-replace-entity", (newEntity) => {
      selectEntity(newEntity);

      replaceEntity(mapEntitiesForHighlighting(newEntity));
    });

    instance.$mount();

    return instance.$el;
  };

  const highlighting = ref<Highlighting>(
    new Highlighting(
      title,
      answer.entities.map(mapEntitiesForHighlighting),
      entityComponentFactory,
      {
        entitiesGap: 9,
      }
    )
  );

  watch(
    () => answer.entities,
    () => {
      const selected = answer.entities.find((e) => e.isSelected);

      selectEntity(selected);
    },
    { deep: true }
  );

  watch(
    () => highlighting.value.spans,
    (spans) => {
      const response = spans.reduce((acc, span) => {
        acc[span.node.id] = acc[span.node.id] || [];

        acc[span.node.id].push({
          from: span.from,
          to: span.to,
          entity: span.entity.id,
        });

        return acc;
      }, {});

      spanQuestion.answer.response({
        value: response,
      });
    }
  );

  onMounted(() => {
    selectEntity(answer.entities[0]);

    highlighting.value.mount();
  });

  onUnmounted(() => {
    highlighting.value.unmount();
  });

  return {
    highlighting,
  };
};
