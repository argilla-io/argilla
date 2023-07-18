import { test, expect } from "@playwright/test";

test.describe("Datasets page", () => {
  test("login successful with correct credentials and get redirect", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.getByPlaceholder("Enter your username").click();

    await page.getByPlaceholder("Enter your username").fill("admin");

    await page.getByPlaceholder("Enter your password").fill("12345678");

    await page.getByRole("button", { name: "Enter" }).click();
    await page.getByRole("button", { name: "Enter" }).click();
    await page.waitForURL("**/datasets");
  });

  test("update url param on filter", async ({ page }) => {
    await page
      .getByRole("listitem")
      .filter({ hasText: "argilla (13)" })
      .locator("div")
      .nth(1)
      .click();
    // TODO : assertion : 1/ expect url to have to param
    // await expect(page).toHaveURL(/datasets?workspaces=argilla);

    await page
      .getByRole("listitem")
      .filter({ hasText: "daniel (3)" })
      .locator("div")
      .nth(1)
      .click();
    // TODO : assertion 2/ expect url to have both param
    // await expect(page).toHaveURL(/datasets?workspaces=argilla,daniel);

    await page
      .getByRole("listitem")
      .filter({ hasText: "TextClassification (1)" })
      .locator("div")
      .nth(1)
      .click();
    // TODO : assertion 3/ expect url to have previous workspace param & new param for task column
    // await expect(page).toHaveURL(/datasets?workspaces=argilla,daniel&tasks=TextClassification);

    await page
      .getByRole("listitem")
      .filter({ hasText: "daniel (3)" })
      .getByRole("img")
      .click();
    // TODO : assertion 4/ expect url to have param workspace with only one item (argilla and no more daniel)
    // await expect(page).toHaveURL(/datasets?workspaces=argilla&tasks=TextClassification);

    await page
      .getByRole("listitem")
      .filter({ hasText: "argilla (13)" })
      .getByRole("img")
      .click();
    // TODO : assertion 5/ expect no workspace param in url
    // await expect(page).toHaveURL(/datasets?tasks=TextClassification);

    await page.getByText("argilla (13)").click();
    // TODO : assertion 6/ we can click on text also to add new query param from filter
    // await expect(page).toHaveURL(/datasets?workspaces=argilla&tasks=TextClassification);

    await page
      .getByText(
        "description: This dataset contains text2text records with 10 predictions (0)"
      )
      .click();
    // TODO : assertion 7/expect to be able to filter by tags
    // await expect(page).toHaveURL(/datasets?workspaces=argilla&tasks=TextClassification&tags=);
  });
});
