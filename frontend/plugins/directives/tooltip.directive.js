import Vue from "vue";

// NOTE - to use tooltip directive, add to your html element where to put a tooltip :
//  v-tooltip="{ content: tooltipMessage, backgroundColor: '#FFF', borderColor: '#FFF', tooltipPosition: 'bottom' }"
//    => content (String) the message to show in the tooltip
//    => backgroundColor (String) the background color of the tooltip
//    => borderColor (String) the border colon of the tooltip (bottom, top, right, left) =>
// TODO - implement the other tooltip direction top/right/left

Vue.directive("tooltip", {
  inserted: (element, binding) => {
    const tooltipId = `${element.id}tooltip`;
    const tooltipCloseIconId = `${tooltipId}__close-icon`;
    let tooltip = null;
    let closeIcon = null;
    element.style.position = "relative";
    element.style.cursor = "pointer";
    let elementOffset = initElementOffset(element);
    const {
      content,
      backgroundColor,
      borderColor,
      color,
      width = 208,
      tooltipPosition = TOOLTIP_DIRECTION.BOTTOM,
    } = binding.value;

    if (content?.length) {
      // NOTE - init tooltip node
      tooltip = document.createElement("div");
      tooltip.setAttribute("id", tooltipId);

      // NOTE - init text node
      const text = document.createTextNode(`${content}`);
      let textWrapper = document.createElement("span");
      textWrapper.appendChild(text);

      // NOTE - init close icon
      let tooltipHeader = document.createElement("div");
      tooltipHeader = initTooltipHeaderStyle(tooltipHeader);
      tooltipHeader.firstChild.setAttribute("id", tooltipCloseIconId);

      // NOTE - triangle
      let tooltipTriangle = document.createElement("div");
      tooltipTriangle = initTooltipTriangleStyle(tooltipTriangle);
      let tooltipTriangleInner = document.createElement("div");
      tooltipTriangleInner =
        initTooltipTriangleInnerStyle(tooltipTriangleInner);

      // NOTE - include close icon and text node inside tooltip
      tooltip.appendChild(tooltipHeader);
      tooltip.appendChild(tooltipTriangle);
      tooltip.appendChild(textWrapper);
      tooltipTriangle.appendChild(tooltipTriangleInner);

      // NOTE - text styles
      textWrapper = initTextStyle(textWrapper, color);

      // NOTE - tooltip styles
      tooltip = initTooltipStyle(tooltip, backgroundColor, borderColor, width);

      // NOTE - init tooltip position
      tooltip = initTooltipPosition(
        tooltip,
        tooltipPosition,
        elementOffset,
        width
      );

      // NOTE - add the tooltip to the element and add event listener to the close icon
      element.appendChild(tooltip);
      element.textWrapper = textWrapper;
      closeIcon = document.getElementById(tooltipCloseIconId);
    }

    element.openTooltip = () => {
      tooltip.style.display = "flex";
      tooltip.setAttribute("tooltip-visible", "true");
      elementOffset = initElementOffset(element);
      tooltip = initTooltipPosition(
        tooltip,
        tooltipPosition,
        elementOffset,
        width
      );
    };

    element.closeTooltip = () => {
      tooltip.style.display = "none";
      tooltip.setAttribute("tooltip-visible", "false");
    };

    element.clickOnTooltipElementEvent = () => {
      if (tooltip.getAttribute("tooltip-visible") === "true") {
        return element.closeTooltip();
      }

      element.openTooltip();
    };

    element.clickOnClose = (event) => {
      event.stopPropagation();
      element.closeTooltip();
    };

    element.clickOutsideEvent = function (event) {
      if (!(element == event.target || element.contains(event.target))) {
        element.closeTooltip();
      }
    };
    element.scrollInParent = function () {
      const { top: parentOffsetTop = 0, bottom: parentOffsetBottom = 0 } =
        initElementOffset(getScrollableParent(element)) || {};
      if (
        elementOffset.top < parentOffsetTop ||
        elementOffset.bottom > parentOffsetBottom
      ) {
        tooltip.style.visibility = "hidden";
      } else {
        tooltip.style.visibility = "visible";
      }
      elementOffset = initElementOffset(element);
      tooltip = initTooltipPosition(
        tooltip,
        tooltipPosition,
        elementOffset,
        width
      );
    };

    // NOTE - init all eventListeners
    initEventsListener(element, closeIcon);

    if (binding?.value.open) element.clickOnTooltipElementEvent();
  },
  unbind: (element) => {
    destroyEventsListener(element);
  },
  update(element, binding) {
    element.textWrapper.innerText = binding?.value.content;

    if (binding?.value.open) {
      element.openTooltip();
    } else {
      element.closeTooltip();
    }
  },
});
const isScrollable = function (element) {
  const hasScrollableContent = element.scrollHeight > element.clientHeight;

  const overflowYStyle = window.getComputedStyle(element).overflowY;
  const isOverflowHidden = overflowYStyle.indexOf("hidden") !== -1;

  return hasScrollableContent && !isOverflowHidden;
};

const initElementOffset = function (element) {
  return element.getBoundingClientRect() || null;
};
const getScrollableParent = function (element) {
  return !element || element === document.body
    ? document.body
    : getElementOrParent(element);
};
const getElementOrParent = function (element) {
  return isScrollable(element)
    ? element
    : getScrollableParent(element.parentNode);
};
const initEventsListener = (element, closeIcon) => {
  if (element && closeIcon) {
    closeIcon.addEventListener("click", element.clickOnClose);
    element.addEventListener("click", element.clickOnTooltipElementEvent);
    document.body.addEventListener("click", element.clickOutsideEvent);
    getScrollableParent(element).addEventListener(
      "scroll",
      element.scrollInParent
    );
  }
};

const destroyEventsListener = (element) => {
  document.body.removeEventListener(
    "click",
    element.clickOnTooltipElementEvent
  );
  document.body.removeEventListener(
    "touchstart",
    element.clickOnTooltipElementEvent
  );
  document.body.removeEventListener("click", element.clickOutsideEvent);
  document.body.removeEventListener("touchstart", element.clickOutsideEvent);
  document.body.removeEventListener("click", element.clickOnClose);
  document.body.removeEventListener("touchstart", element.clickOnClose);
  getScrollableParent(element).removeEventListener(
    "scroll",
    element.scrollInParent
  );
};

const initTooltipStyle = (
  tooltip,
  backgroundColor = "white",
  borderColor = "transparent",
  width
) => {
  tooltip.style.position = "fixed";
  tooltip.style.width = `${width}px`;
  tooltip.style.display = "none";
  tooltip.style.flexDirection = "column";
  tooltip.style.zIndex = "99999";
  tooltip.style.backgroundColor = backgroundColor;
  tooltip.style.borderRadius = "5px";
  tooltip.style.padding = "16px";
  tooltip.style.boxShadow = "0 8px 20px 0 rgba(0,0,0,.2)";
  tooltip.style.transition = "opacity 0.3s ease 0.2s";
  tooltip.style.border = `2px ${borderColor} solid`;
  tooltip.style.cursor = "default";
  return tooltip;
};
const initTooltipHeaderStyle = (tooltipHeader) => {
  tooltipHeader.style.display = "flex";
  tooltipHeader.style.justifyContent = "flex-end";
  tooltipHeader.style.marginBottom = "8px";
  tooltipHeader.innerHTML =
    '<svg width="20" height="20" viewBox="0 0 41 40" fill="none" xmlns="http://www.w3.org/2000/svg" style="cursor: pointer; width: 14px; height: 14px;"><path d="M8.9225 5.58721C8.13956 4.80426 6.87015 4.80426 6.08721 5.58721C5.30426 6.37015 5.30426 7.63956 6.08721 8.4225L17.6647 20L6.08733 31.5774C5.30438 32.3603 5.30438 33.6297 6.08733 34.4127C6.87027 35.1956 8.13968 35.1956 8.92262 34.4127L20.5 22.8353L32.0774 34.4127C32.8603 35.1956 34.1297 35.1956 34.9127 34.4127C35.6956 33.6297 35.6956 32.3603 34.9127 31.5774L23.3353 20L34.9128 8.4225C35.6957 7.63956 35.6957 6.37015 34.9128 5.58721C34.1298 4.80426 32.8604 4.80426 32.0775 5.58721L20.5 17.1647L8.9225 5.58721Z" fill="#9a9a9a"/></svg>';
  return tooltipHeader;
};

const initTooltipTriangleStyle = (tooltipTriangle) => {
  tooltipTriangle.style.position = "absolute";
  tooltipTriangle.style.left = "50%";
  tooltipTriangle.style.transform = "translateX(-50%)";
  tooltipTriangle.style.top = "0";
  return tooltipTriangle;
};
const initTooltipTriangleInnerStyle = (tooltipTriangleInner) => {
  tooltipTriangleInner.style.position = "relative";
  tooltipTriangleInner.style.width = "0";
  tooltipTriangleInner.style.height = "0";
  tooltipTriangleInner.style.top = "-10px";
  tooltipTriangleInner.style.borderBottom = "10px solid white";
  tooltipTriangleInner.style.borderRight = "10px solid transparent";
  tooltipTriangleInner.style.borderLeft = "10px solid transparent";
  return tooltipTriangleInner;
};

const initTooltipPosition = (
  tooltip,
  tooltipPosition,
  elementOffset,
  width
) => {
  const margin = 8;
  switch (tooltipPosition.toUpperCase()) {
    case TOOLTIP_DIRECTION.BOTTOM:
      tooltip.style.top = `${
        elementOffset.y + elementOffset.height + margin
      }px`;
      tooltip.style.left = `${
        elementOffset.left - width / 2 + elementOffset.width / 2
      }px`;
      break;
    default:
    // tooltip direction is unknown
  }
  return tooltip;
};

const initTextStyle = (textWrapper, color = "rgba(0, 0, 0, 0.87)") => {
  textWrapper.style.textAlign = "left";
  textWrapper.style.fontSize = "13px";
  textWrapper.style.fontStyle = "normal";
  textWrapper.style.fontWeight = "300";
  textWrapper.style.lineHeight = "18px";
  textWrapper.style.whiteSpace = "pre-wrap";
  textWrapper.style.overflow = "auto";
  textWrapper.style.maxHeight = "250px";
  textWrapper.style.color = `${color}`;
  return textWrapper;
};

const TOOLTIP_DIRECTION = Object.freeze({
  BOTTOM: "BOTTOM",
});
