import { onMounted, ref, watch } from "vue-demi";
import { Highlighting } from "../../questions/form/span/components/highlighting";
import { Question } from "~/v1/domain/entities/question/Question";

export const useSpanAnnotationTextFieldViewModel = ({
  spanQuestion,
  title,
}: {
  spanQuestion: Question;
  title: string;
}) => {
  const classByGroup = spanQuestion.answer.entities.reduce((acc, entity, i) => {
    acc[entity.name] = `hl-${i + 1}`;
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
    () => spanQuestion.answer.entities,
    () => {
      highlighting.value.entity = spanQuestion.answer.entities.find(
        (e) => e.isSelected
      )?.name;
    },
    { deep: true }
  );

  onMounted(() => {
    highlighting.value.mount();
    highlighting.value.entity = spanQuestion.answer.entities[0].name;
  });

  return {
    highlighting,
  };
};
