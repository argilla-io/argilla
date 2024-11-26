import Vue from "vue";

Vue.directive("circle", {
  bind: (element, binding) => {
    let circleDiameter = "0px";
    let fontSize = "1rem";
    let borderColor = "var(--bg-opacity-1)";

    const { size } = binding?.value ?? { size: "SMALL" };

    switch (size) {
      case "MINI":
        circleDiameter = "26px";
        fontSize = "0.6rem";
        borderColor = "var(--color-avatar-fg)";
        break;
      case "SMALL":
        circleDiameter = "34px";
        fontSize = "1rem";
        break;
      case "MEDIUM":
        circleDiameter = "45px";
        break;
      default:
        circleDiameter = "34px";
    }

    element.style.display = "flex";
    element.style.alignItems = "center";
    element.style.justifyContent = "center";
    element.style.height = circleDiameter;
    element.style.width = circleDiameter;
    element.style.borderRadius = "50%";
    element.style.border = `1px solid ${borderColor}`;
    element.style.fontSize = fontSize;
    element.style.fontWeight = "500";
    element.style.lineHeight = circleDiameter;
    element.style.textTransform = "uppercase";
  },
});
