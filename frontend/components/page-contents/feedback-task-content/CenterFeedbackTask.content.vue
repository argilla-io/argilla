<template>
  <div class="wrapper">
    <div class="container">
      <div class="record">
        <div class="item" v-for="field in record.fields" :key="field.title">
          <div class="title-area --body1">
            <span v-text="field.title"></span>
          </div>
          <div class="content" v-html="field.text" />
        </div>
      </div>
      <QuestionsFormComponent :initialInputs="inputs" />
    </div>
  </div>
</template>

<script>
export default {
  name: "CenterFeedbackTaskContent",
  created() {
    this.record = {
      id: "daboudi",
      fields: [
        {
          title: "Input",
          text: `
            Lorem ipsum dolor sit amet consectetur adipisicing elit.
            Dolorum ratione quas quis eveniet harum cum, earum a facere
            voluptate fugit nostrum sequi facilis incidunt debitis unde?
            Eos rem debitis velit? Officia magni odit possimus quis nisi.
            Dolore, eaque eligendi! Beatae quos debitis soluta distinctio
            qui ex sint nesciunt non quidem laboriosam. Veniam ex accusantium
            explicabo ab, pariatur id sapiente tenetur.`,
        },
        {
          title: "Outputs",
          text: `
            Lorem ipsum dolor sit amet, consectetur adipisicing elit.
            Vitae cupiditate fugit quos officiis expedita, deleniti libero
            inventore fugiat perferendis dolor optio praesentium enim molestiae
            molestias. <br /><br />Ipsam perferendis aperiam perspiciatis assumenda. Numquam
            reprehenderit non distinctio repellat adipisci laborum, fugit sint
            labore nulla tempore quam eos iste asperiores eius laudantium vel
            similique officiis sunt vero beatae magni ab dicta! Culpa, qui
            dolore. <br /><br />Quaerat, repellendus deserunt doloribus laudantium ducimus
            atque quia rerum ullam. <br /><br />Sit veritatis, quas id sed culpa deleniti
            officiis ipsa laudantium, eos qui pariatur iure facere, sequi
            delectus similique! Commodi, a. <br /><br />Totam illo iure iste voluptate?
            Veritatis blanditiis est rem? Ipsam consequatur incidunt obcaecati
            distinctio qui beatae quaerat, ullam sit voluptas facere repellat
            accusamus dolorem iure aliquam fugit veritatis nesciunt modi.
            Dolore corrupti assumenda tenetur soluta et? Laborum nemo repellendus
            architecto necessitatibus accusamus nesciunt exercitationem neque
            dicta! Dolore sed atque nam sit ea earum quia minima, veniam natus
            non hic necessitatibus. <br /><br />Quibusdam repudiandae odit eaque enim
            voluptatem fugiat hic quidem voluptate, sint id quae a? Perferendis
            ad suscipit reiciendis dolor omnis corrupti quos porro aliquid
            recusandae. <br /><br />Ipsam doloribus esse debitis libero. <br /><br />Quod corporis
            eveniet cupiditate aliquid, iure sed dignissimos repellat architecto
            quaerat impedit animi porro saepe ipsa molestiae quibusdam
            suscipit nam. <br /><br />Fuga quo sunt itaque corrupti atque dolores fugit,
            eligendi voluptate.`,
        },
      ],
    };
    this.inputs = [
      // {
      //   id: "id_1",
      //   question:
      //     "Are the instruction and input adequate for the capabilities of this model?",
      //   outputs: [
      //     { id: 1, value: true, text: "Yes" },
      //     { id: 2, value: false, text: "No" },
      //   ],
      //   default: null,
      //   required: true,
      //   componentType: "SINGLE_LABEL",
      // },
      // {
      //   id: "id_2",
      //   question: "Does the output contain hallucinated or untruthful facts?",
      //   outputs: [
      //     { id: 1, value: true, text: "Yes" },
      //     { id: 2, value: false, text: "No" },
      //   ],
      //   default: null,
      //   componentType: "SINGLE_LABEL",
      // },
      // {
      //   id: "id_3",
      //   question:
      //     "Select any labels that apply to the content found in the text:",
      //   outputs: [
      //     { id: 1, text: "Not English", label: "Not English" },
      //     { id: 2, text: "Not Appropriate", label: "Not Appropriate" },
      //     { id: 3, text: "Contains PII", label: "Contains PII" },
      //     { id: 4, text: "Hate Speech", label: "Hate Speech" },
      //     { id: 5, text: "Sexual Content", label: "Sexual Content" },
      //     { id: 6, text: "Daboudi", label: "Daboudi" },
      //     { id: 7, text: "Dabouda", label: "Dabouda" },
      //     { id: 8, text: "Patati", label: "Patati" },
      //     { id: 9, text: "Patata", label: "Patata" },
      //     { id: 10, text: "baguette", label: "baguette" },
      //     { id: 11, text: "pain au chocolat", label: "pain au chocolat" },
      //     { id: 12, text: "croissant", label: "croissant" },
      //   ],
      //   default: null,
      //   componentType: "SINGLE_LABEL",
      // },
      // {
      //   id: "id_4",
      //   question: "Rate the overall quality of the output",
      //   outputs: [
      //     { id: 1, value: 1, text: "1" },
      //     { id: 2, value: 2, text: "2" },
      //     { id: 3, value: 3, text: "3" },
      //     { id: 4, value: 4, text: "4" },
      //     { id: 5, value: 5, text: "5" },
      //   ],
      //   default: null,
      //   componentType: "SINGLE_LABEL",
      // },
      {
        id: "id_5",
        question:
          "Rate the helpfulness of the output (1-not helpful, 7-very helpful):",
        outputs: [
          { id: 1, value: true, text: "1" },
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
        question:
          "Rate the harmlessness of the output (1-very harmful, 5-harmless):",
        outputs: [
          { id: "id_6-1", value: false, text: "1" },
          { id: "id_6-2", value: false, text: "2" },
          { id: "id_6-3", value: false, text: "3" },
          { id: "id_6-4", value: false, text: "4" },
          { id: "id_6-5", value: true, text: "5" },
        ],
        required: false,
        tooltipMessage: "This is a tooltipz",
        componentType: "RATING",
      },
      {
        id: "id_7",
        question: "Comment",
        outputs: { text: "dadadadda", placeholder: "this is the placeholder" },
        default: null,
        required: false,
        tooltipMessage: "This is a tooltip",
        componentType: "FREE_TEXT",
      },
    ];
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-wrap: wrap;
  gap: 2 * $base-space;
}
.record {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space 4 * $base-space 2 * $base-space 4 * $base-space;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
}

.item {
  display: flex;
  flex-direction: column;
  padding: 2 * $base-space;
  background: #f5f5f5;
  border-radius: 8px;
  .title-area {
    display: flex;
    align-items: center;
    gap: $base-space;
    color: rgba(0, 0, 0, 0.37);
  }
}
</style>
