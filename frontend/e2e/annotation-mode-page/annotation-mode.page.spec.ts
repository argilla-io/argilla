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

      await page.getByPlaceholder("Search labels").first().fill("v");

      await expect(page).toHaveScreenshot();
    });
    test("user press just letter V and go automatically to search bar and can update this text", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.getByPlaceholder("Search labels").first().fill("v");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().press("Backspace");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().fill("Pos");
      await expect(page).toHaveScreenshot();
    });
    test("user can delete the search with backspace, write another search query and submit with shift+enter, ", async ({
      page,
    }) => {
      const record = await goToAnnotationPage(page);
      await mockRecordResponses(page, record.id, "submitted");

      await page.getByPlaceholder("Search labels").first().fill("v");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().press("Backspace");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().fill("Pos");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Space");

      await page.getByText("Very Positive").first().press("Shift+Enter");

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
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Space");

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

      await page.getByPlaceholder("Search labels").first().fill("v");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().press("Backspace");
      await expect(page).toHaveScreenshot();
      await page.getByPlaceholder("Search labels").first().fill("Pos");
      await expect(page).toHaveScreenshot();

      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Tab");
      await page.keyboard.press("Space");

      await page.getByText("Very Positive").first().press("Shift+Backspace");

      await expect(page).toHaveScreenshot();
    });

    test("after the user filter labels can move to other option and select one pressing Space key", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.getByPlaceholder("Search labels").first().fill("v");

      await page.getByPlaceholder("Search labels").first().press("Tab");
      await page.locator("#sentiment_positive").press("Tab");
      await page.locator("#sentiment_very_positive").press("Tab");

      await page.keyboard.type(" ");

      await expect(page).toHaveScreenshot();
    });

    test("after the user filter labels can move to other option and select one pressing Space key and go to next question when user click in other option", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.getByPlaceholder("Search labels").first().fill("v");
      await page.getByPlaceholder("Search labels").first().press("Tab");
      await page.locator("#sentiment_positive").press("Tab");
      await page.locator("#sentiment_very_positive").press("Tab");
      await page.keyboard.type(" ");

      await page.getByText("Loving").click();

      await expect(page).toHaveScreenshot();
    });

    test("expand collapsable label", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Tab");
      await page.locator("#sentiment_very_positive").press("Tab");
      await page.locator("#sentiment_negative").press("Tab");
      await page.locator("#sentiment_neutral").press("Tab");
      await page.locator("#sentiment_happy").press("Tab");
      await page.locator("#sentiment_sad").press("Tab");
      await page.locator("#sentiment_angry").press("Tab");
      await page.locator("#sentiment_excited").press("Tab");
      await page.locator("#sentiment_disappointed").press("Tab");
      await page.locator("#sentiment_surprised").press("Tab");
      await page.getByLabel("Grateful").press("Tab");
      await page.getByLabel("Loving").press("Tab");
      await page.getByLabel("Optimistic").press("Tab");
      await page.getByLabel("Proud").press("Tab");
      await page.getByLabel("Worried").press("Tab");
      await page.getByLabel("Hopeful").press("Tab");
      await page.getByLabel("Bored").press("Tab");

      await expect(page).toHaveScreenshot();
    });

    test("go to next question with shift and arrow down", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question with shift and arrow up", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowUp");

      await expect(page).toHaveScreenshot();
    });

    test("the user move as a loop with tab key", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Tab");
      await page.locator("#sentiment_very_positive").press("Tab");
      await page.locator("#sentiment_negative").press("Tab");
      await page.locator("#sentiment_neutral").press("Tab");
      await page.locator("#sentiment_happy").press("Tab");
      await page.locator("#sentiment_sad").press("Tab");
      await page.locator("#sentiment_angry").press("Tab");
      await page.locator("#sentiment_excited").press("Tab");
      await page.locator("#sentiment_disappointed").press("Tab");
      await page.locator("#sentiment_surprised").press("Tab");
      await page.getByLabel("Grateful").press("Tab");
      await page.getByLabel("Loving").press("Tab");
      await page.getByLabel("Optimistic").press("Tab");
      await page.getByLabel("Proud").press("Tab");
      await page.getByLabel("Worried").press("Tab");
      await page.getByLabel("Hopeful").press("Tab");
      await page.getByLabel("Bored").press("Tab");
      await page.getByLabel("Amused").press("Tab");
      await page.getByLabel("Confused").press("Tab");
      await page.getByLabel("Frustrated").press("Tab");
      await page.getByLabel("Content").press("Tab");
      await page.getByLabel("Over the Moon").press("Tab");
      await page.getByLabel("Heartbroken").press("Tab");
      await page.getByLabel("Furious").press("Tab");
      await page.getByLabel("Ecstatic").press("Tab");
      await page.getByLabel("Devastated").press("Tab");
      await page.getByLabel("Anxious").press("Tab");
      await page.getByLabel("Terrified").press("Tab");
      await page.getByLabel("Delighted").press("Tab");
      await page.getByLabel("Disgusted").press("Tab");
      await page.getByLabel("Jealous").press("Tab");
      await page.getByLabel("Lonely").press("Tab");
      await page.getByLabel("Shocked").press("Tab");
      await page.getByLabel("Satisfied").press("Tab");
      await page.getByLabel("Relaxed").press("Tab");
      await page.getByLabel("Thankful").press("Tab");
      await page.getByLabel("Annoyed").press("Tab");
      await page.getByLabel("Guilty").press("Tab");
      await page.getByLabel("Embarrassed").press("Tab");
      await page.getByLabel("Ashamed").press("Tab");
      await page.getByLabel("Pessimistic").press("Tab");
      await page.getByLabel("Nostalgic").press("Tab");
      await page.getByLabel("Sympathetic").press("Tab");
      await page.getByLabel("Fearful").press("Tab");
      await page.getByLabel("Hurt").press("Tab");
      await page.locator("#sentiment_positive").press("Tab");
      await page.locator("#sentiment_very_positive").press("Tab");
      await page.locator("#sentiment_negative").press("Tab");

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Multi component", () => {
    test("go to multilabel component", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page.locator("#sentiment-multi-label_positive").press("v");

      await expect(page).toHaveScreenshot();
    });

    test("expand collapsable when the user try to find other label", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page.locator("#sentiment-multi-label_positive").press("Tab");
      await page.locator("#sentiment-multi-label_very_positive").press("Tab");
      await page.locator("#sentiment-multi-label_negative").press("Tab");
      await page.locator("#sentiment-multi-label_neutral").press("Tab");
      await page.locator("#sentiment-multi-label_happy").press("Tab");
      await page.locator("#sentiment-multi-label_sad").press("Tab");
      await page.locator("#sentiment-multi-label_angry").press("Tab");
      await page.locator("#sentiment-multi-label_excited").press("Tab");
      await page.locator("#sentiment-multi-label_disappointed").press("Tab");
      await page.locator("#sentiment-multi-label_surprised").press("Tab");
      await page.getByLabel("Grateful").press("Tab");
      await page.getByLabel("Loving").press("Tab");
      await page.getByLabel("Optimistic").press("Tab");

      await page.getByText("Negative").nth(1).click();
      await page.getByText("Neutral").nth(1).click();

      await expect(page).toHaveScreenshot();
    });

    test("the user move as a loop inside multilabel component", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment-multi-label_positive").press("Tab");
      await page.locator("#sentiment-multi-label_very_positive").press("Tab");
      await page.locator("#sentiment-multi-label_negative").press("Tab");
      await page.locator("#sentiment-multi-label_neutral").press("Tab");
      await page.locator("#sentiment-multi-label_happy").press("Tab");
      await page.locator("#sentiment-multi-label_sad").press("Tab");
      await page.locator("#sentiment-multi-label_angry").press("Tab");
      await page.locator("#sentiment-multi-label_excited").press("Tab");
      await page.locator("#sentiment-multi-label_disappointed").press("Tab");
      await page.locator("#sentiment-multi-label_surprised").press("Tab");
      await page.locator("#sentiment-multi-label_grateful").press("Tab");
      await page.locator("#sentiment-multi-label_loving").press("Tab");
      await page.locator("#sentiment-multi-label_optimistic").press("Tab");
      await page.locator("#sentiment-multi-label_proud").press("Tab");
      await page.locator("#sentiment-multi-label_worried").press("Tab");
      await page.locator("#sentiment-multi-label_hopeful").press("Tab");
      await page.locator("#sentiment-multi-label_bored").press("Tab");
      await page.locator("#sentiment-multi-label_amused").press("Tab");
      await page.locator("#sentiment-multi-label_confused").press("Tab");
      await page.locator("#sentiment-multi-label_frustrated").press("Tab");
      await page.locator("#sentiment-multi-label_content").press("Tab");
      await page.locator("#sentiment-multi-label_over_the_moon").press("Tab");
      await page.locator("#sentiment-multi-label_heartbroken").press("Tab");
      await page.locator("#sentiment-multi-label_furious").press("Tab");
      await page.locator("#sentiment-multi-label_ecstatic").press("Tab");
      await page.locator("#sentiment-multi-label_devastated").press("Tab");
      await page.locator("#sentiment-multi-label_anxious").press("Tab");
      await page.locator("#sentiment-multi-label_terrified").press("Tab");
      await page.locator("#sentiment-multi-label_delighted").press("Tab");
      await page.locator("#sentiment-multi-label_disgusted").press("Tab");
      await page.locator("#sentiment-multi-label_jealous").press("Tab");
      await page.locator("#sentiment-multi-label_lonely").press("Tab");
      await page.locator("#sentiment-multi-label_shocked").press("Tab");
      await page.locator("#sentiment-multi-label_satisfied").press("Tab");
      await page.locator("#sentiment-multi-label_relaxed").press("Tab");
      await page.locator("#sentiment-multi-label_thankful").press("Tab");
      await page.locator("#sentiment-multi-label_annoyed").press("Tab");
      await page.locator("#sentiment-multi-label_guilty").press("Tab");
      await page.locator("#sentiment-multi-label_embarrassed").press("Tab");
      await page.locator("#sentiment-multi-label_ashamed").press("Tab");
      await page.locator("#sentiment-multi-label_pessimistic").press("Tab");
      await page.locator("#sentiment-multi-label_nostalgic").press("Tab");
      await page.locator("#sentiment-multi-label_sympathetic").press("Tab");
      await page.locator("#sentiment-multi-label_fearful").press("Tab");
      await page.locator("#sentiment-multi-label_hurt").press("Tab");
      await page.locator("#sentiment-multi-label_positive").press("Tab");
      await page.locator("#sentiment-multi-label_very_positive").press("Tab");
      await page.locator("#sentiment-multi-label_negative").press("Tab");
      await page.locator("#sentiment-multi-label_neutral").press("Tab");

      await expect(page).toHaveScreenshot();
    });

    test("go to next question with shift and arrow down", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");

      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question with shift and arrow up", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");

      await page.getByLabel("1").press("Shift+ArrowUp");

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Rating component", () => {
    test("go to rating component with keyboard", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");

      await expect(page).toHaveScreenshot();
    });

    test("when the user click in the option go automatically to next question", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");

      await page.locator("label").filter({ hasText: "2" }).click();

      await page
        .getByText("This is a review of the review")
        .press("Meta+Shift+ArrowRight");

      await page.getByText("This is a review of the review").fill("TEST");

      await expect(page).toHaveScreenshot();
    });

    test("when user complete rating with keyboard automatically go to next question", async ({
      page,
    }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");

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

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");
      await page.getByLabel("1").press("Shift+ArrowDown");

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question with keyboard", async ({ page }) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");
      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");
      await page.getByLabel("1").press("Shift+ArrowDown");

      await page
        .getByText("This is a review of the review")
        .press("Shift+ArrowUp");

      await expect(page).toHaveScreenshot();
    });
  });

  test.describe("Ranking component", () => {
    const goToRankingComponent = async (page: Page) => {
      await goToAnnotationPage(page);

      await page.locator("#sentiment_positive").press("Shift+ArrowDown");

      await page
        .locator("#sentiment-multi-label_positive")
        .press("Shift+ArrowDown");

      await page.getByLabel("1").press("Shift+ArrowDown");

      await page
        .getByText("This is a review of the review")
        .press("Shift+ArrowDown");
    };

    test("go to ranking component with keyboard", async ({ page }) => {
      await goToRankingComponent(page);

      await expect(page).toHaveScreenshot();
    });

    test("go to previous question if the user is in ranking component with keyboard", async ({
      page,
    }) => {
      await goToRankingComponent(page);

      await page.getByTitle("Option A").press("Shift+ArrowUp");

      await page
        .getByText("This is a review of the review")
        .press("Meta+Shift+ArrowRight");

      await page.getByText("This is a review of the review").fill("TEST");

      await expect(page).toHaveScreenshot();
    });

    test("order ranking question options", async ({ page }) => {
      await goToRankingComponent(page);

      await page.getByTitle("Option A").press("2");

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

      await page.getByTitle("Option A").press("2");

      await page.waitForTimeout(300);

      await page.getByTitle("Option B").press("1");

      await page.waitForTimeout(300);

      await page.getByTitle("Option C").press("4");
      await page.waitForTimeout(300);

      await page.getByTitle("Option D").press("3");

      await page.waitForTimeout(300);

      await expect(page).toHaveScreenshot();
    });

    test("move as a loop in ranking component", async ({ page }) => {
      await goToRankingComponent(page);

      await page.getByText("✨ Ranking (optional)").press("Tab");
      await expect(page).toHaveScreenshot();

      await page.getByText("✨ Ranking (optional)").press("Tab");
      await page.getByText("✨ Ranking (optional)").press("Tab");
      await expect(page).toHaveScreenshot();

      await page.getByText("✨ Ranking (optional)").press("Tab");
      await page.getByText("✨ Ranking (optional)").press("Tab");
      await page.getByText("✨ Ranking (optional)").press("Tab");
      await expect(page).toHaveScreenshot();

      await page.getByText("✨ Ranking (optional)").press("Shift+Tab");
      await expect(page).toHaveScreenshot();
    });

    test("move as a loop in ranking component with some ranked and other unranked", async ({
      page,
    }) => {
      await goToRankingComponent(page);

      await page.getByText("✨ Ranking (optional)").press("Tab");
      await expect(page).toHaveScreenshot();

      await page.getByText("✨ Ranking (optional)").press("Backspace");
      await page.getByText("Ranking (optional)").press("Tab");
      await page.getByText("Ranking (optional)").press("Backspace");
      await expect(page).toHaveScreenshot();

      await page.getByText("Ranking (optional)").press("Tab");
      await page.getByText("Ranking (optional)").press("Tab");
      await page.getByText("Ranking (optional)").press("Tab");
      await expect(page).toHaveScreenshot();

      await page.getByText("Ranking (optional)").press("Shift+Tab");
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
