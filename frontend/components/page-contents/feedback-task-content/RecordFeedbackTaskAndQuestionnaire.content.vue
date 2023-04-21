<template>
  <div class="wrapper">
    <RecordFeedbackTaskComponent v-if="record" :record="record" />
    <QuestionsFormComponent
      v-if="questionsWithRecordAnswers && questionsWithRecordAnswers.length"
      :initialInputs="questionsWithRecordAnswers"
    />
  </div>
</template>

<script>
import { getQuestionsByDatasetId } from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import { getRecordWithFieldsByDatasetId } from "@/models/feedback-task-model/record/record.queries";
import { getRecordResponsesByRecordId } from "@/models/feedback-task-model/record-response/recordResponse.queries";

export default {
  name: "RecordFeedbackTaskAndQuestionnaireComponent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
    orderBy: {
      type: Object,
      default: () => {
        return { orderQuestionBy: "order", ascendent: true };
      },
    },
    recordOffset: {
      type: Number,
      required: true,
    },
  },
  computed: {
    record() {
      return getRecordWithFieldsByDatasetId(this.datasetId, this.recordOffset);
    },
    userId() {
      return this.$auth.user.id;
    },
    recordResponses() {
      if (this.record && this.userId)
        return getRecordResponsesByRecordId({
          userId: this.userId,
          recordId: this.record.id,
        });
    },
    questions() {
      if (this.record)
        return getQuestionsByDatasetId(
          this.datasetId,
          this.orderBy?.orderQuestionsBy,
          this.orderBy?.ascendent
        );
    },
    questionsWithRecordAnswers() {
      if (this.record) {
        const newOptionsByQuestion = this.factoryNewOptionsByQuestion();
        return this.factoryQuestionsWithRecordAnswer(newOptionsByQuestion);
      }
    },
  },
  methods: {
    factoryQuestionsWithRecordAnswer(newOptionsByQuestion) {
      const questionsWithRecordAnswers = this.questions.map((question) => {
        const newOptions =
          newOptionsByQuestion.find(
            (recordResponseByQuestion) =>
              recordResponseByQuestion.question_name === question.name
          )?.newOptions || question.options;
        return { ...question, options: newOptions };
      });

      return questionsWithRecordAnswers;
    },
    factoryNewOptionsByQuestion() {
      const newOptionsByQuestion = [];
      this.questions.forEach((question) => {
        this.recordResponses.forEach((response) => {
          if (response.question_name === question.name) {
            const newOptions = question.options.map((output) => {
              const recordResponseOutputWithSameTextAsInQuestionOutput =
                response.options.find(
                  (responseOutput) => responseOutput.id === output.id
                );

              if (recordResponseOutputWithSameTextAsInQuestionOutput) {
                return recordResponseOutputWithSameTextAsInQuestionOutput;
              }
              return output;
            });

            newOptionsByQuestion.push({
              question_name: question.name,
              newOptions,
            });
          }
        });
      });

      return newOptionsByQuestion;
    },
  },
};
</script>

<style lang="scss" scoped>
.wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 2 * $base-space;
}
</style>
