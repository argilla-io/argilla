import { onMounted } from "vue";
import { Question } from "~/v1/domain/entities/question/Question";
import { SpanQuestionAnswer } from "~/v1/domain/entities/question/QuestionAnswer";

interface SpanAnnotationImageFieldProps {
  imageURL: string;
  spanQuestion: Question;
}

type EntitySelected = {
  id: string;
  value: string;
  text: string;
  color: string;
};
type UISpan = {
  entity: EntitySelected;
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
};

export const useSpanAnnotationImageField = ({
  imageURL,
  spanQuestion,
}: SpanAnnotationImageFieldProps) => {
  const img = new Image();
  let annotations: UISpan[] =
    JSON.parse(localStorage.getItem("annotations")) || [];
  let currentRect: UISpan = null;
  let entitySelected: EntitySelected = null;

  let isDrawing = false;
  let canvas;
  let context;
  let startX;
  let startY;

  onMounted(() => {
    canvas = document.getElementById("canvas") as HTMLCanvasElement;
    context = canvas.getContext("2d");

    img.src = imageURL;

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;
      context.drawImage(img, 0, 0);
      drawAnnotations();
    };

    canvas.addEventListener("mousedown", (e) => {
      startX = e.offsetX;
      startY = e.offsetY;
      isDrawing = true;
      const answer = spanQuestion.answer as SpanQuestionAnswer;
      entitySelected = answer.options.find((e) => e.isSelected);
      if (!entitySelected) return;

      currentRect = {
        x: startX,
        y: startY,
        width: 0,
        height: 0,
        entity: {
          ...entitySelected,
        },
        id: createID(),
      };
    });

    canvas.addEventListener("mousemove", (e) => {
      if (isDrawing) {
        const currentX = e.offsetX;
        const currentY = e.offsetY;
        currentRect.width = currentX - startX;
        currentRect.height = currentY - startY;

        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(img, 0, 0);

        drawAnnotations();

        drawRectangle(currentRect);
      }
    });

    canvas.addEventListener("mouseup", () => {
      isDrawing = false;

      addNewAnnotation(currentRect);

      drawAnnotations();

      saveAnnotations();
    });

    canvas.addEventListener("mouseout", () => {
      isDrawing = false;
    });
  });

  const removeAnnotation = (rect) => {
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.drawImage(img, 0, 0);

    annotations = annotations.filter((r) => r.id !== rect.id);
    saveAnnotations();

    drawAnnotations();
  };

  const addNewAnnotation = (rect) => {
    if (rect.width === 0 || rect.height === 0) {
      return;
    }

    if (rect.width < 0) {
      rect.x += rect.width;
      rect.width *= -1;
    }

    if (rect.height < 0) {
      rect.y += rect.height;
      rect.height *= -1;
    }

    if (!entitySelected) return;

    annotations = [
      ...annotations,
      {
        id: createID(),
        entity: {
          ...entitySelected,
        },
        ...rect,
      },
    ];

    saveAnnotations();
  };

  const drawAnnotations = () => {
    clearButtons();
    clearText();
    annotations.forEach((rect) => {
      drawRectangle(rect);

      drawDeleteButton(rect);
      drawText(rect);
    });
  };

  const saveAnnotations = () => {
    localStorage.setItem("annotations", JSON.stringify(annotations));
  };

  const createID = () => {
    return Math.random().toString(36).substring(2, 9);
  };

  const drawRectangle = (rect: UISpan) => {
    context.beginPath();
    context.rect(rect.x, rect.y, rect.width, rect.height);
    context.strokeStyle = rect.entity.color;
    context.lineWidth = 2;
    context.stroke();
  };

  const drawDeleteButton = (rect: UISpan) => {
    const btn = document.createElement("button");
    btn.className = "delete-btn";
    btn.innerText = "X";
    btn.style.left = `${canvas.offsetLeft + rect.x + rect.width - 10}px`;
    btn.style.top = `${canvas.offsetTop + rect.y - 10}px`;
    btn.onclick = () => {
      removeAnnotation(rect);
    };

    document.getElementById("span-image-field-container").appendChild(btn);
  };

  const drawText = (rect: UISpan) => {
    const p = document.createElement("p");
    p.className = "annotation-text";
    p.innerText = rect.entity.text;
    p.style.left = `${canvas.offsetLeft + rect.x}px`;
    p.style.top = `${canvas.offsetTop + rect.y + rect.height + 5}px`;
    document.getElementById("span-image-field-container").appendChild(p);
  };

  const clearButtons = () => {
    const buttons = document.querySelectorAll(".delete-btn");
    buttons.forEach((button) => button.remove());
  };

  const clearText = () => {
    const texts = document.querySelectorAll(".annotation-text");
    texts.forEach((text) => text.remove());
  };

  // const clearAll = () => {
  //   annotations.forEach((rect) => {
  //     removeAnnotation(rect);
  //   });

  //   clearText();
  //   clearButtons();
  // };
};
