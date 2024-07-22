import { Field } from "../entities/field/Field";
import { Question } from "../entities/question/Question";
import { Suggestion } from "../entities/question/Suggestion";
import { RecordAnswer } from "../entities/record/RecordAnswer";
import { RecordCriteria } from "../entities/record/RecordCriteria";
import { IRecordStorage } from "../services/IRecordStorage";
import {
  EmptyQueueRecords,
  Records,
  RecordsWithReference,
} from "../entities/record/Records";
import { Record } from "../entities/record/Record";
import { IQuestionRepository } from "../services/IQuestionRepository";
import {
  FieldRepository,
  RecordRepository,
} from "~/v1/infrastructure/repositories";

export class GetRecordsByCriteriaUseCase {
  constructor(
    private readonly recordRepository: RecordRepository,
    private readonly questionRepository: IQuestionRepository,
    private readonly fieldRepository: FieldRepository,
    private readonly recordsStorage: IRecordStorage
  ) {}

  public async execute(criteria: RecordCriteria): Promise<Records> {
    const { datasetId, queuePage } = criteria;
    const savedRecords = this.recordsStorage.get();
    savedRecords.synchronizeQueuePagination(criteria);

    const getRecords = this.recordRepository.getRecords(criteria);
    const getQuestions = this.questionRepository.getQuestions(datasetId);
    const getFields = this.fieldRepository.getFields(datasetId);

    const [recordsFromBackend, questionsFromBackend, fieldsFromBackend] =
      await Promise.all([getRecords, getQuestions, getFields]);

    if (recordsFromBackend.records.length === 0) {
      return new EmptyQueueRecords(
        criteria,
        questionsFromBackend.map((question) => {
          return new Question(
            question.id,
            question.name,
            question.description,
            datasetId,
            question.title,
            question.required,
            question.settings
          );
        })
      );
    }

    const recordsToAnnotate = recordsFromBackend.records.map(
      (record, index) => {
        const recordPage = index + queuePage;

        const fields = fieldsFromBackend
          .filter((f) => record.fields[f.name])
          .map((field) => {
            return new Field(
              field.id,
              field.name,
              field.title,
              record.fields[field.name],
              datasetId,
              field.required,
              field.settings
            );
          });

        const questions = questionsFromBackend.map((question) => {
          return new Question(
            question.id,
            question.name,
            question.description,
            datasetId,
            question.title,
            question.required,
            question.settings
          );
        });

        const userAnswer = record.responses[0];
        const answer = userAnswer
          ? new RecordAnswer(
              userAnswer.id,
              userAnswer.status,
              userAnswer.values,
              userAnswer.updated_at
            )
          : null;

        const suggestions = record.suggestions
          .map((suggestion) => {
            const question = questions.find(
              (q) => q.id === suggestion.question_id
            );

            if (criteria.page.isBulkMode && !question.isSpanType)
              return undefined;

            return new Suggestion(
              suggestion.id,
              suggestion.question_id,
              question.type,
              suggestion.value,
              suggestion.score,
              suggestion.agent
            );
          })
          .filter(Boolean);

        return new Record(
          record.id,
          datasetId,
          questions,
          fields,
          answer,
          suggestions,
          record.query_score,
          recordPage,
          record.metadata,
          record.status,
          record.inserted_at,
          record.updated_at
        );
      }
    );

    if (criteria.isFilteringBySimilarity) {
      let referenceRecord = savedRecords.getById(
        criteria.similaritySearch.recordId
      );

      if (!referenceRecord) {
        const referenceRecordFromBackend =
          await this.recordRepository.getRecord(
            criteria.similaritySearch.recordId
          );

        const fields = fieldsFromBackend
          .filter((f) => referenceRecordFromBackend.fields[f.name])
          .map((field) => {
            return new Field(
              field.id,
              field.name,
              field.title,
              referenceRecordFromBackend.fields[field.name],
              datasetId,
              field.required,
              field.settings
            );
          });

        referenceRecord = new Record(
          referenceRecordFromBackend.id,
          datasetId,
          [],
          fields,
          null,
          [],
          0,
          0,
          referenceRecordFromBackend.metadata,
          referenceRecordFromBackend.status,
          referenceRecordFromBackend.inserted_at,
          referenceRecordFromBackend.updated_at
        );
      }

      return new RecordsWithReference(
        recordsToAnnotate,
        recordsFromBackend.total,
        referenceRecord
      );
    }

    return new Records(recordsToAnnotate, recordsFromBackend.total);
  }
}
