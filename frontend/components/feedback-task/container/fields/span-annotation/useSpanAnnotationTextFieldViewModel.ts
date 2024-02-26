import { onMounted, onUnmounted, ref, watch } from "vue-demi";
import { Highlighting } from "./components/highlighting";
import { colorGenerator } from "./components/color-generator";
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

  const highlighting = ref<Highlighting>(
    new Highlighting(title, answer.entities.map(mapEntitiesForHighlighting), {
      entityClassName: "highlight__entity",
      entitiesGap: 9,
    })
  );

  watch(
    () => answer.entities,
    () => {
      const selected = answer.entities.find((e) => e.isSelected);

      highlighting.value.changeEntity(mapEntitiesForHighlighting(selected));
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
    const firstEntity = answer.entities[0];
    firstEntity.isSelected = true;

    highlighting.value.changeEntity(mapEntitiesForHighlighting(firstEntity));

    highlighting.value.mount();
  });

  onUnmounted(() => {
    highlighting.value.unmount();
  });

  return {
    highlighting,
  };
};
