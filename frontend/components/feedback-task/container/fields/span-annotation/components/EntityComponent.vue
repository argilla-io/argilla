<template>
  <div>
    {{ selectedEntity }}
  </div>
</template>

<script>
export default {
  name: "EntityComponent",
  props: {
    selectedEntity: {
      type: Object,
      required: true,
    },
  },
};
</script>
