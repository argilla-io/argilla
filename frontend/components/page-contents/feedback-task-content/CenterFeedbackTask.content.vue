<template>
  <RecordFeedbackTaskAndQuestionnaireContent
    :datasetId="datasetId"
    :recordOffset="currentPage"
    :key="currentPage"
  />
</template>

<script>
import { upsertDatasetQuestions } from "@/models/feedback-task-model/dataset-question/datasetQuestion.queries";
import { upsertRecords } from "@/models/feedback-task-model/record/record.queries";
export default {
  name: "CenterFeedbackTaskContent",
  props: {
    datasetId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      currentPage: 0,
    };
  },
  created() {
    // TODO - INITIALS records and inputs, will be replaced by API values
    const records = [
      {
        id: "record_1",
        recordStatus: "discard",
        responses: [
          {
            record_id: "record_1",
            question_id: "id_5",
            options: [{ id: 1, value: true, text: "1" }],
          },
          {
            record_id: "record_1",
            question_id: "id_6",
            options: [{ id: "id_6-4", value: true, text: "4" }],
          },
        ],
        fields: [
          {
            id: "field_1",
            title: "Input",
            text: `
            Lorem ipsum dolor sit amet consectetur adipisicing elit.
            Dolorum ratione quas quis eveniet harum cum, earum a facere
            voluptate fugit nostrum sequi facilis incidunt debitis unde?
            Eos rem debitis velit? Officia magni odit possimus quis nisi.
            Dolore, eaque eligendi! Beatae quos debitis soluta distinctio
            qui ex sint nesciunt non quidem laboriosam. Veniam ex accusantium
            explicabo ab, pariatur id sapiente tenetur.
            `,
          },
          {
            id: "field_2",
            title: "Output",
            text: `
            Lorem ipsum dolor sit amet, consectetur adipisicing elit.
            Vitae cupiditate fugit quos officiis expedita, deleniti libero
            inventore fugiat perferendis dolor optio praesentium enim molestiae
            molestias. Ipsam perferendis aperiam perspiciatis assumenda. Numquam
            reprehenderit non distinctio repellat adipisci laborum, fugit sint
            labore nulla tempore quam eos iste asperiores eius laudantium vel
            similique officiis sunt vero beatae magni ab dicta! Culpa, qui
            dolore. Quaerat, repellendus deserunt doloribus laudantium ducimus
            atque quia rerum ullam. Sit veritatis, quas id sed culpa deleniti
            officiis ipsa laudantium, eos qui pariatur iure facere, sequi
            delectus similique! Commodi, a. Totam illo iure iste voluptate?
            Veritatis blanditiis est rem? Ipsam consequatur incidunt obcaecati
            distinctio qui beatae quaerat, ullam sit voluptas facere repellat
            accusamus dolorem iure aliquam fugit veritatis nesciunt modi.
            Dolore corrupti assumenda tenetur soluta et? Laborum nemo repellendus
            architecto necessitatibus accusamus nesciunt exercitationem neque
            dicta! Dolore sed atque nam sit ea earum quia minima, veniam natus
            non hic necessitatibus. Quibusdam repudiandae odit eaque enim
            voluptatem fugiat hic quidem voluptate, sint id quae a? Perferendis
            ad suscipit reiciendis dolor omnis corrupti quos porro aliquid
            recusandae. Ipsam doloribus esse debitis libero. Quod corporis
            eveniet cupiditate aliquid, iure sed dignissimos repellat architecto
            quaerat impedit animi porro saepe ipsa molestiae quibusdam
            suscipit nam. Fuga quo sunt itaque corrupti atque dolores fugit,
            eligendi voluptate.`,
          },
        ],
      },
      {
        id: "record_2",
        responses: [
          {
            record_id: "record_2",
            question_id: "id_6",
            options: [{ id: "id_6-5", value: true, text: "5" }],
          },
          {
            record_id: "record_2",
            question_id: "id_7",
            options: [
              {
                id: "patati",
                value: "I m blue daboudi dabouda",
                text: "I m blue daboudi dabouda",
              },
            ],
          },
        ],
        fields: [
          {
            id: "field_3",
            title: "Input",
            text: `
            Lorem ipsum dolor sit amet consectetur adipisicing elit.
            Dolorum ratione quas quis eveniet harum cum, earum a facere
            voluptate fugit nostrum sequi facilis incidunt debitis unde?
            Eos rem debitis velit? Officia magni odit possimus quis nisi.
            Dolore, eaque eligendi! Beatae quos debitis soluta distinctio
            qui ex sint nesciunt non quidem laboriosam. Veniam ex accusantium
            explicabo ab, pariatur id sapiente tenetur.
            `,
          },
          {
            id: "field_4",
            title: "Output",
            text: `
            Lorem ipsum dolor sit amet, consectetur adipisicing elit.
            Vitae cupiditate fugit quos officiis expedita, deleniti libero
            inventore fugiat perferendis dolor optio praesentium enim molestiae
            molestias. Ipsam perferendis aperiam perspiciatis assumenda. Numquam
            reprehenderit non distinctio repellat adipisci laborum, fugit sint
            labore nulla tempore quam eos iste asperiores eius laudantium vel
            similique officiis sunt vero beatae magni ab dicta! Culpa, qui
            dolore. Quaerat, repellendus deserunt doloribus laudantium ducimus
            atque quia rerum ullam. Sit veritatis, quas id sed culpa deleniti
            officiis ipsa laudantium, eos qui pariatur iure facere, sequi
            delectus similique! Commodi, a. Totam illo iure iste voluptate?
            Veritatis blanditiis est rem? Ipsam consequatur incidunt obcaecati
            distinctio qui beatae quaerat, ullam sit voluptas facere repellat
            accusamus dolorem iure aliquam fugit veritatis nesciunt modi.
            Dolore corrupti assumenda tenetur soluta et? Laborum nemo repellendus
            architecto necessitatibus accusamus nesciunt exercitationem neque
            dicta! Dolore sed atque nam sit ea earum quia minima, veniam natus
            non hic necessitatibus. Quibusdam repudiandae odit eaque enim
            voluptatem fugiat hic quidem voluptate, sint id quae a? Perferendis
            ad suscipit reiciendis dolor omnis corrupti quos porro aliquid
            recusandae. Ipsam doloribus esse debitis libero. Quod corporis
            eveniet cupiditate aliquid, iure sed dignissimos repellat architecto
            quaerat impedit animi porro saepe ipsa molestiae quibusdam
            suscipit nam. Fuga quo sunt itaque corrupti atque dolores fugit,
            eligendi voluptate.`,
          },
          {
            id: "field_5",
            title: "Second options",
            text: `
            Lorem ipsum dolor sit amet, consectetur adipisicing elit.
            Vitae cupiditate fugit quos officiis expedita, deleniti libero
            inventore fugiat perferendis dolor optio praesentium enim molestiae
            molestias. Ipsam perferendis aperiam perspiciatis assumenda. Numquam
            reprehenderit non distinctio repellat adipisci laborum, fugit sint
            labore nulla tempore quam eos iste asperiores eius laudantium vel
            similique officiis sunt vero beatae magni ab dicta! Culpa, qui
            dolore. Quaerat, repellendus deserunt doloribus laudantium ducimus
            atque quia rerum ullam. Sit veritatis, quas id sed culpa deleniti
            officiis ipsa laudantium, eos qui pariatur iure facere, sequi
            delectus similique! Commodi, a. Totam illo iure iste voluptate?
            Veritatis blanditiis est rem? Ipsam consequatur incidunt obcaecati
            distinctio qui beatae quaerat, ullam sit voluptas facere repellat
            accusamus dolorem iure aliquam fugit veritatis nesciunt modi.
            Dolore corrupti assumenda tenetur soluta et? Laborum nemo repellendus
            architecto necessitatibus accusamus nesciunt exercitationem neque
            dicta! Dolore sed atque nam sit ea earum quia minima, veniam natus
            non hic necessitatibus. Quibusdam repudiandae odit eaque enim
            voluptatem fugiat hic quidem voluptate, sint id quae a? Perferendis
            ad suscipit reiciendis dolor omnis corrupti quos porro aliquid
            recusandae. Ipsam doloribus esse debitis libero. Quod corporis
            eveniet cupiditate aliquid, iure sed dignissimos repellat architecto
            quaerat impedit animi porro saepe ipsa molestiae quibusdam
            suscipit nam. Fuga quo sunt itaque corrupti atque dolores fugit,
            eligendi voluptate.`,
          },
        ],
      },
    ];
    const inputs = [
      // {
      //   id: "id_1",
      //   question:
      //     "Are the instruction and input adequate for the capabilities of this model?",
      //   options: [
      //     { id: 1, value: true, text: "Yes" },
      //     { id: 2, value: false, text: "No" },
      //   ],
      //   default: null,
      //   required: true,
      //   componentType: "SINGLE_LABEL",
      //   tooltipMessage: null,
      // },
      {
        id: "id_5",
        name: "nameOfQuestion_id_5",
        question:
          "Rate the helpfulness of the output (1-not helpful, 7-very helpful):",
        options: [
          { id: 1, value: false, text: "1" },
          { id: 2, value: false, text: "2" },
          { id: 3, value: false, text: "3" },
          { id: 4, value: false, text: "4" },
          { id: 5, value: false, text: "5" },
          { id: 6, value: false, text: "6" },
          { id: 7, value: false, text: "7" },
        ],
        required: true,
        componentType: "RATING",
      },
      {
        id: "id_6",
        name: "nameOfQuestion_id_6",
        question:
          "Rate the harmlessness of the output (1-very harmful, 5-harmless):",
        options: [
          { id: "id_6-1", value: false, text: "1" },
          { id: "id_6-2", value: false, text: "2" },
          { id: "id_6-3", value: false, text: "3" },
          { id: "id_6-4", value: false, text: "4" },
          { id: "id_6-5", value: false, text: "5" },
        ],
        required: false,
        tooltipMessage: "This is a tooltipz",
        componentType: "RATING",
      },
      {
        id: "id_7",
        name: "nameOfQuestion_id_7",
        question: "Comment",
        placeholder: "this is the placeholder",
        options: [
          {
            id: "patati",
            text: "",
            value: "",
          },
        ],
        default: null,
        required: true,
        tooltipMessage: "This is a tooltip",
        componentType: "FREE_TEXT",
      },
    ];

    // FORMAT records and questions in good orm shapes
    const formattedRecords = this.factoryRecordsForOrm(records);
    const formattedQuestions = this.factoryQuestionsForOrm(inputs);

    // UPSERT records and questions in ORM
    upsertRecords(formattedRecords);
    upsertDatasetQuestions(formattedQuestions);

    this.onBusEventIsLoadingLabels();
  },
  methods: {
    onBusEventIsLoadingLabels() {
      this.$root.$on("current-page", (currentPage) => {
        //NOTE - the pagination start at 1 but the record start at 1 => there is an offset of 1 to remove
        this.currentPage = currentPage - 1;
      });
    },
    factoryRecordsForOrm(records) {
      return records.map((record) => {
        return {
          ...record,
          record_id: record.id,
          dataset_id: this.datasetId,
          record_status: record.recordStatus,
          record_fields: record.fields,
          record_responses: record.responses,
        };
      });
    },
    factoryQuestionsForOrm(initialQuestions) {
      return initialQuestions.map((question, index) => {
        return {
          ...question,
          dataset_id: this.datasetId,
          order: index,
          component_type: question.componentType,
          is_required: question.required,
          tooltip_message: question.tooltipMessage,
        };
      });
    },
  },
  destroyed() {
    this.$root.$off("current-page");
  },
};
</script>
