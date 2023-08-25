import { test, expect, Page } from "@playwright/test";
import {
  loginUserAndWaitFor,
  mockAllDatasets,
  newDatasetsMocked,
  mockRecord,
  mockRecordWith12Ranking,
  mockRecordWithRating,
  mockRecordResponses,
  mockRecordForLongAndShortQuestion,
} from "../common";

const shortcuts = Object.freeze({
  clear: "",
  discard: "Shift+Backspace",
  submit: "Shift+Enter",
  goToNextQuestion: "Shift+ArrowDown",
  goToPrevQuestion: "Shift+ArrowUp",
  singleLabel: {
    select: "Space",
    goToNextLabel: "Tab"
  },
  multiLabel: {
    select: "Space",
    goToNextLabel: "Tab"
  }
})

const goToAnnotationPage = async (page, shortAndLongQuestions = false) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  const record = shortAndLongQuestions
    ? await mockRecordForLongAndShortQuestion(page, {
      datasetId: dataset.id,
      workspaceId: dataset.workspace_id,
    })
    : await mockRecord(page, {
      datasetId: dataset.id,
      workspaceId: dataset.workspace_id,
    });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(2000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(3000);

  return record;
};

const goToAnnotationPageWith12Ranking = async (page: Page) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  await mockRecordWith12Ranking(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(1000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(1000);
};

const goToAnnotationPageWith10Rating = async (page) => {
  const dataset = newDatasetsMocked[0];

  await mockAllDatasets(page);
  await mockRecordWithRating(page, {
    datasetId: dataset.id,
    workspaceId: dataset.workspace_id,
  });

  await loginUserAndWaitFor(page, "datasets");

  await page.waitForTimeout(2000);

  await page.getByRole("link", { name: dataset.name }).click();

  await page.waitForTimeout(3000);
};

test.use({
  viewport: { width: 1600, height: 1400 },
});

test.describe("Annotate page", () => {
  test("go to annotation mode page", async ({ page }) => {
    await goToAnnotationPage(page);

    await expect(page).toHaveScreenshot();
  });

  test("filter by workspaces from annotation page", async ({ page }) => {
    await goToAnnotationPage(page);

    await page.getByRole("link", { name: "argilla" }).click();

    await expect(page).toHaveScreenshot();
  });

  test("hide spark icon when user change suggested answer", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page.getByText("Very Positive").first().click();

    await expect(page).toHaveScreenshot();
  });

  test("show spark icon when user change suggested answer and go back to default", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page.getByText("Positive").first().click();

    await expect(page).toHaveScreenshot();
  });

  test("disable submit when user no complete required answer", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page.getByText("Positive").nth(1).click();

    await expect(page).toHaveScreenshot();
  });

  test("disable submit when user complete partially ranking question", async ({
    page,
  }) => {
    await goToAnnotationPage(page);

    await page
      .getByTitle("Option A")
      .dragTo(page.locator(".draggable__questions-container"));

    await expect(page).toHaveScreenshot();
  });

  test("can drag and drop ranking question", async ({ page }) => {
    await goToAnnotationPage(page);

    await page.getByTitle("Option A").click();

    await page.mouse.down();

    await expect(page).toHaveScreenshot();

    await page.mouse.up();

    await page.getByRole("button", { name: "Clear" }).click();

    await page.getByTitle("Option A").click();

    await page.mouse.down();

    await expect(page).toHaveScreenshot();
  });

  test("clear all questions", async ({ page }) => {
    await goToAnnotationPage(page);

    await page.getByRole("button", { name: "Clear" }).click();

    await expect(page).toHaveScreenshot();

    await page
      .getByText("Review Rating", { exact: true })
      .scrollIntoViewIfNeeded();

    await expect(page).toHaveScreenshot();

    await page.getByText("Ranking", { exact: true }).scrollIntoViewIfNeeded();

    await expect(page).toHaveScreenshot();
  });

  test("clear all questions and discard the record", async ({ page }) => {
    const record = await goToAnnotationPage(page);
    await mockRecordResponses(page, record.id, "discarded");

    await page.getByRole("button", { name: "Clear" }).click();

    await page.getByRole("button", { name: "Discard" }).click();

    await page.waitForTimeout(2000);

    await expect(page).toHaveScreenshot();
  });

  test("label with just one character", async ({ page }) => {
    await goToAnnotationPage(page, true);

    await expect(page).toHaveScreenshot();
  });

  test("focus on first question when click on form (where there is no in question)", async ({
    page,
  }) => {
    await goToAnnotationPage(page);
    const formBox = await page.getByText("Submit your feedback").boundingBox();

    await page.mouse.click(formBox.x - 25, formBox.y - 25); // click outside form to loose focus
    await expect(page).toHaveScreenshot();

    await page.mouse.click(formBox.x + 5, formBox.y + 5);
    await page.waitForTimeout(400);

    await expect(page).toHaveScreenshot();
  });

  test("focus on question clicked when user click outside of form and click in a question again", async ({
    page,
  }) => {
    await goToAnnotationPage(page);
    const formBox = await page.getByText("Submit your feedback").boundingBox();

    await page.mouse.click(formBox.x - 25, formBox.y - 25); // click outside form to loose focus
    await expect(page).toHaveScreenshot();

    await page.getByText("Negative").nth(1).click();
    await page.waitForTimeout(400);

    await expect(page).toHaveScreenshot();
  });
});

test.describe("Annotation page shortcuts", () => {
  test.describe("Single component", () => {
    test("user press just letter V and go automatically to search bar and filter data", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("v");

      await expect(page).toHaveScreenshot();
    });
    test("user press just letter V and go automatically to search bar and can update this text", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("v");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Backspace");
      await expect(page).toHaveScreenshot();

      await page.keyboard.insertText("Pos");
      await expect(page).toHaveScreenshot();
    });
    test("user can delete the search with backspace, write another search query and submit with shift+enter, ", async ({
      page,
    }) => {
      const record = await goToAnnotationPage(page);
      await mockRecordResponses(page, record.id, "submitted");

      await page.keyboard.press("v");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Backspace");
      await expect(page).toHaveScreenshot();

      await page.keyboard.insertText("Pos");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.select);

      await page.keyboard.press(shortcuts.submit);

      await expect(page).toHaveScreenshot();
    });

    test.skip("user can delete the search with backspace, write another search query and clear with shift+space, ", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.getByPlaceholder("Search labels").first().fill("v");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().press("Backspace");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().fill("Pos");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.select);

      // TODO: find way to simulate Spacebar
      await page.keyboard.down("Shift");
      await page.getByText("Very Positive").first().press("Space");
      await page.keyboard.up("Shift");
      await page.waitForTimeout(200);

      await expect(page).toHaveScreenshot();
    });
    test("user can delete the search with backspace, write another search query and discard with shift+backspace, ", async ({
      page,
    }) => {
      const record = await goToAnnotationPage(page);
      await mockRecordResponses(page, record.id, "discarded");

      await page.keyboard.press("v");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Backspace");
      await expect(page).toHaveScreenshot();

      await page.keyboard.insertText("Pos");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.select);

      await page.keyboard.press(shortcuts.discard);

      await expect(page).toHaveScreenshot();
    });

    test("after the user filter labels can move to other option and select one pressing Space key", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("v");

      await page.keyboard.press("Tab");
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);

      await page.keyboard.press(shortcuts.singleLabel.select);

      await expect(page).toHaveScreenshot();
    });

    test("after the user filter labels can move to other option and select one pressing Space key and go to next question when user click in other option", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("v");
      await page.keyboard.press("Tab");
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.select);

      await page.getByText("Loving").click();

      await expect(page).toHaveScreenshot();
    });

    test("expand collapsable label", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);

      await expect(page).toHaveScreenshot();
    });

    test("go to next question with shift and arrow down", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.goToNextQuestion);

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question with shift and arrow up", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.goToNextQuestion);
      await page.keyboard.press(shortcuts.goToPrevQuestion);

      await expect(page).toHaveScreenshot();
    });

    test("the user move as a loop with tab key", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.singleLabel.goToNextLabel);

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Multi component", () => {
    test("go to multilabel component", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.goToNextQuestion);
      await page.keyboard.press("v");

      await expect(page).toHaveScreenshot();
    });

    test("expand collapsable when the user try to find other label", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.goToNextQuestion);

      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);

      await expect(page).toHaveScreenshot();

      await page.getByText("Negative").nth(1).click();
      await page.getByText("Neutral").nth(1).click();

      await expect(page).toHaveScreenshot();
    });

    test("the user move as a loop inside multilabel component", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.goToNextQuestion);

      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);
      await page.keyboard.press(shortcuts.multiLabel.goToNextLabel);

      await expect(page).toHaveScreenshot();
    });

    test("go to next question with shift and arrow down", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.goToNextQuestion);

      await page.keyboard.press(shortcuts.goToNextQuestion);

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question with shift and arrow up", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press(shortcuts.goToNextQuestion);
      await page.keyboard.press(shortcuts.goToNextQuestion);

      await page.keyboard.press(shortcuts.goToPrevQuestion);

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Rating component", () => {
    test("go to rating component with keyboard", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("Shift+ArrowDown");
      await page.keyboard.press("Shift+ArrowDown");

      await expect(page).toHaveScreenshot();
    });

    test("when the user click in the option go automatically to next question", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("Shift+ArrowDown");
      await page.keyboard.press("Shift+ArrowDown");

      await page.locator("label").filter({ hasText: "2" }).click();

      await page.keyboard.press("Meta+Shift+ArrowRight");

      await page.keyboard.insertText("TEST");

      await expect(page).toHaveScreenshot();
    });

    test("when user complete rating with keyboard automatically go to next question", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("Shift+ArrowDown");
      await page.keyboard.press("Shift+ArrowDown");

      await page.keyboard.press("4");

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Rating component with 10 options", () => {
    test("go to rating component with keyboard", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);

      await expect(page).toHaveScreenshot();
    });
    test("rating value 1 by pressing 1", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);
      await page.keyboard.press("1");
      await expect(page).toHaveScreenshot();
    });
    test("rating value 5 by pressing 5", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);
      await page.keyboard.press("5");
      await expect(page).toHaveScreenshot();
    });
    test("rating value 10 by pressing 10", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);
      await page.keyboard.press("1");
      await page.keyboard.press("0");
      await expect(page).toHaveScreenshot();
    });
    test("user can not rating with invalid key", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);

      await page.keyboard.press("?");

      await expect(page).toHaveScreenshot();
    });
    test("rating with non existing number", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);

      await page.keyboard.press("2");
      await page.keyboard.press("2");

      await expect(page).toHaveScreenshot();
    });
    test("un rate question if the user press twice the same key", async ({
      page,
    }) => {
      await goToAnnotationPageWith10Rating(page);

      await page.keyboard.press("2");

      await page.waitForTimeout(400);

      await page.keyboard.press("2");

      await expect(page).toHaveScreenshot();
    });
    test("user can not rating if press any non digit key", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);

      await page.keyboard.press("u");

      await expect(page).toHaveScreenshot();
    });
    test("user can not rating with value zero", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);

      await page.keyboard.press("0");

      await expect(page).toHaveScreenshot();
    });
    test("rating a question too fast key press", async ({ page }) => {
      await goToAnnotationPageWith10Rating(page);

      await page.keyboard.press("1");
      await page.keyboard.press("2");

      await page.waitForTimeout(400);

      await page.keyboard.press("1");
      await page.keyboard.press("0");

      await page.waitForTimeout(400);

      await expect(page).toHaveScreenshot();

      await page.keyboard.press("2");

      await page.waitForTimeout(400);

      await expect(page).toHaveScreenshot();

      await page.keyboard.press("8");

      await page.waitForTimeout(400);

      await expect(page).toHaveScreenshot();

      await page.keyboard.press("1");
      await page.keyboard.press("0");

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Text component", () => {
    test("go to text component with keyboard", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("Shift+ArrowDown");
      await page.keyboard.press("Shift+ArrowDown");
      await page.keyboard.press("Shift+ArrowDown");

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question with keyboard", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("Shift+ArrowDown");
      await page.keyboard.press("Shift+ArrowDown");
      await page.keyboard.press("Shift+ArrowDown");

      await page
        .getByText("This is a review of the review")
        .press("Shift+ArrowUp");

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Ranking component", () => {
    const goToRankingComponent = async (page: Page) => {
      await goToAnnotationPage(page);

      await page.keyboard.press("Shift+ArrowDown");

      await page.keyboard.press("Shift+ArrowDown");

      await page.keyboard.press("Shift+ArrowDown");

      await page.keyboard.press("Shift+ArrowDown");
    };

    test("go to ranking component with keyboard", async ({ page }) => {
      await goToRankingComponent(page);

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question if the user is in ranking component with keyboard", async ({
      page,
    }) => {
      await goToRankingComponent(page);

      await page.keyboard.press("Shift+ArrowUp");

      await page.keyboard.press("Meta+Shift+ArrowRight");

      await page.keyboard.insertText("TEST");

      await expect(page).toHaveScreenshot();
    });

    test("order ranking question options", async ({ page }) => {
      await goToRankingComponent(page);

      await page.keyboard.press("2");

      await expect(page).toHaveScreenshot();
    });

    test("reset order ranking question options", async ({ page }) => {
      await goToRankingComponent(page);

      await page
        .getByTitle("Option A")
        .dragTo(page.locator(".draggable__questions-container"));

      await page
        .getByTitle("Option B")
        .dragTo(page.locator(".draggable__questions-container"));

      await page
        .getByTitle("Option C")
        .dragTo(page.locator(".draggable__questions-container"));

      await page
        .getByTitle("Option D")
        .dragTo(page.locator(".draggable__questions-container"));

      await expect(page).toHaveScreenshot();
    });

    test("reorder ranking question options", async ({ page }) => {
      await goToRankingComponent(page);

      await page.keyboard.press("2");

      await page.waitForTimeout(300);

      await page.keyboard.press("1");

      await page.waitForTimeout(300);

      await page.keyboard.press("4");
      await page.waitForTimeout(300);

      await page.keyboard.press("3");

      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot();
    });

    test("move as a loop in ranking component", async ({ page }) => {
      await goToRankingComponent(page);

      await page.keyboard.press("Tab");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Shift+Tab");
      await expect(page).toHaveScreenshot();
    });

    test("move as a loop in ranking component with some ranked and other unranked", async ({
      page,
    }) => {
      await goToRankingComponent(page);

      await page.keyboard.press("Tab");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Backspace");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Backspace");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Shift+Tab");
      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Ranking component with 12 slots", () => {
    test("go to ranking component with keyboard", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);

      await expect(page).toHaveScreenshot();
    });

    test("move to slot 10 by pressing 10", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);
      await page.keyboard.press("1");
      await page.keyboard.press("0");

      await expect(page).toHaveScreenshot();
    });

    test("move to slot 11 by pressing 11", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);
      await page.keyboard.press("1");
      await page.keyboard.press("1");

      await expect(page).toHaveScreenshot();
    });

    test("move to slot 12 by pressing 12", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);
      await page.keyboard.press("1");
      await page.keyboard.press("2");

      await expect(page).toHaveScreenshot();
    });

    test("move to slot 1 by pressing 1", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);
      await page.keyboard.press("1");
      await expect(page).toHaveScreenshot();
    });

    test("unrank a question by pressing Backspace", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);
      await page.keyboard.press("1");

      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot();

      await page.waitForTimeout(500);

      await page.keyboard.press("Shift+Tab");
      await page.keyboard.press("Backspace");

      await expect(page).toHaveScreenshot();
    });

    test("clear form answers after unrank", async ({ page }) => {
      await goToAnnotationPageWith12Ranking(page);
      await page.keyboard.press("1");

      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot();

      await page.waitForTimeout(500);

      await page.keyboard.press("Shift+Tab");
      await page.keyboard.press("Shift+Space");
      await expect(page).toHaveScreenshot();
    });
  });
});
