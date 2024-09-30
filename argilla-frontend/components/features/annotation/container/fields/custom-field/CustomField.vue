<template>
  <div class="custom_field_component" :key="content">
    <div class="title-area --body2">
      <span class="custom_field_component__title-content" v-text="title" />
      <BaseActionTooltip
        class="custom_field_component__tooltip"
        tooltip="Copied"
        tooltip-position="left"
      >
        <BaseButton
          title="Copy to clipboard"
          class="custom_field_component__copy-button"
          @click.prevent="$copyToClipboard(content)"
        >
          <svgicon color="#acacac" name="copy" width="18" height="18" />
        </BaseButton>
      </BaseActionTooltip>
    </div>
    <div :id="`fields-content-${name}`" class="content-area --body1">
      <Sandbox :content="template" />
    </div>
  </div>
</template>
<script>
/* eslint-disable */
const STYLES = `
<script>
if (parent) {
  const currentHead = document.getElementsByTagName("head")[0];
  const styles = parent.document.getElementsByTagName("style");
  for (const style of styles) {
    currentHead.appendChild(style.cloneNode(true));
  }
}
<\/script>`;

const BASIC_TEMPLATE = `
${STYLES}
<script>const record = #RECORD_OBJECT#;<\/script>
<script src="./js/handlebars.min.js"><\/script>
<div id="template" class="text-center">
  #TEMPLATE#
</div>
<script>
  const template = document.getElementById("template").innerHTML;
  const compiledTemplate = Handlebars.compile(template);
  const html = compiledTemplate({ record });
  document.body.innerHTML = html;
<\/script>
`;
const ADVANCE_TEMPLATE = ` ${STYLES}
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
      required: true,
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
  background: palette(grey, 800);
  border-radius: $border-radius-m;
  &:hover {
    #{$this}__copy-button {
      opacity: 1;
    }
  }
  .title-area {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: $base-space;
    color: var(--fg-secondary);
  }
  .content-area {
    white-space: pre-wrap;
    word-break: break-word;
  }
  &__title-content {
    word-break: break-word;
    width: calc(100% - 30px);
  }
  &__tooltip {
    display: flex;
    align-self: flex-start;
  }
  &__copy-button {
    flex-shrink: 0;
    padding: 0;
    opacity: 0;
  }
}
.fade-enter-active,
.fade-leave-active {
  transition: all 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
