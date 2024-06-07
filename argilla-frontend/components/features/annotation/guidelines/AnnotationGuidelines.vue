<template>
  <RenderMarkdownBaseComponent
    class="--body1 description__text"
    :markdown="guidelines"
  />
</template>

<script>
export default {
  name: "SettingsInfo",
  props: {
    guidelines: {
      type: String,
      required: true,
    },
  },
};
</script>
