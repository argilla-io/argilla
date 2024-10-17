<template>
  <div class="custom_field_component" :key="content">
    <div class="title-area --body2">
      <span class="custom_field_component__title-content" v-text="title" />
    </div>
    <Sandbox :content="template" />
  </div>
</template>
<script>
/* eslint-disable */
const BASIC_TEMPLATE = `
<script>const record = #RECORD_OBJECT#;<\/script>
<script src="./js/handlebars.min.js"><\/script>
<div id="template">
#TEMPLATE#
</div>
<script>
  Handlebars.registerHelper("json", (context) => {
    return new Handlebars.SafeString('<pre style="overflow: auto">' + JSON.stringify(context, null, 4) + '</pre>');
  });

  const template = document.getElementById("template").innerHTML;
  const compiledTemplate = Handlebars.compile(template);
  const html = compiledTemplate({ record });
  document.body.innerHTML = html;
<\/script>
`;
const ADVANCE_TEMPLATE = `
<script>
  const record = #RECORD_OBJECT#;
<\/script>
#TEMPLATE#
`;

export default {
  props: {
    name: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    settings: {
      type: Object,
      required: true,
    },
    content: {
      type: String,
      required: true,
    },
    sdkRecord: {
      type: Object,
      default: () => ({}),
    },
  },
  computed: {
    isAdvanced() {
      return this.settings.advanced_mode;
    },
    template() {
      const recordObject = JSON.stringify(this.sdkRecord);

      const templateToUse = this.isAdvanced ? ADVANCE_TEMPLATE : BASIC_TEMPLATE;

      return templateToUse
        .replace("#RECORD_OBJECT#", recordObject)
        .replace("#TEMPLATE#", this.content);
    },
  },
};
</script>

<style lang="scss" scoped>
.custom_field_component {
  $this: &;
  display: flex;
  flex-direction: column;
  gap: $base-space;
  padding: 2 * $base-space;
  background: var(--bg-field);
  border-radius: $border-radius-m;
  border: 1px solid var(--border-field);
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: var(--fg-secondary);
  }
  &__title-content {
    word-break: break-word;
    width: calc(100% - 30px);
  }
}
</style>
