import { onMounted, ref, watch } from "vue-demi";
import { Highlighting } from "../../questions/form/span/components/highlighting";
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

  const classByGroup = answer.entities.reduce((acc, entity) => {
    acc[entity.name] = `hl-${entity.id}`;
    return acc;
  }, {} as Record<string, string>);

  const highlighting = ref<Highlighting>(
    new Highlighting(title, {
      entitiesCSS: classByGroup,
      entityClassName: "highlight__entity",
      entitiesGap: 9,
    })
  );

  watch(
    () => answer.entities,
    () => {
      highlighting.value.entity = answer.entities.find(
        (e) => e.isSelected
      )?.name;
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
          entity: span.entity,
        });

        return acc;
      }, {});

      spanQuestion.answer.response({
        value: response,
      });
    }
  );

  onMounted(() => {
    highlighting.value.mount();
    const firstEntity = answer.entities[0];

    if (!firstEntity) return;

    firstEntity.isSelected = true;
    highlighting.value.entity = firstEntity.name;
  });

  return {
    highlighting,
  };
};
