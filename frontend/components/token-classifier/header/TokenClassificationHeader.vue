<template>
  <div>
    <filters-area :dataset="dataset" />
    <entities-header :dataset="dataset" />
    <global-actions :dataset="dataset">
      <validate-discard-action
        :dataset="dataset"
        @discard-records="onDiscard"
        @validate-records="onValidate"
      >
      </validate-discard-action>
      <create-new-action @new-label="onNewLabel" />
    </global-actions>
  </div>
</template>
<script>
import { mapActions } from "vuex";
export default {
  props: {
    dataset: {
      required: true,
      type: Object,
    },
  },
  computed: {
    showAnnotationMode() {
      return this.dataset.viewSettings.annotationEnabled;
    },
  },

  methods: {
    ...mapActions({
      discard: "entities/datasets/discardAnnotations",
      validate: "entities/datasets/validateAnnotations",
    }),

    async onDiscard(records) {
      await this.discard({
        dataset: this.dataset,
        records: records,
      });
    },
    async onValidate(records) {
      await this.validate({
        dataset: this.dataset,
        records: records.map((record) => ({
          ...record,
          annotation: {
            ...(record.annotation || record.prediction),
            agent: this.$auth.user,
          },
        })),
      });
    },
    async onNewLabel(label) {
      await this.dataset.$dispatch("setEntities", {
        dataset: this.dataset,
        entities: [
          ...new Set([...this.dataset.entities.map((ent) => ent.text), label]),
        ],
      });
    },
  },
};
</script>
