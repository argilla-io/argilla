import {
  createMetadataMock,
  createMetadataWithNoValuesMock,
} from "../__mocks__/metadata/mock";
import { MetadataFilterList } from "./MetadataFilter";

const find = (metadataFilter: MetadataFilterList, category: string) => {
  return metadataFilter.categories.find((m) => m.name === category);
};

describe("MetadataFilter ", () => {
  describe("Categories", () => {
    test("should return the categories", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const categories = metadataFilter.categories;

      expect(categories.map((n) => n.name)).toEqual([
        "split",
        "loss",
        "float",
        "split_2",
        "split_3",
      ]);
    });
    test("should return empty array if there is no metadata", () => {
      const metadataFilter = new MetadataFilterList([]);
      const categories = metadataFilter.categories;

      expect(categories).toEqual([]);
    });
  });

  describe("FilteredCategories", () => {
    test("should return the categories", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      metadataFilter.commit();

      expect(metadataFilter.filteredCategories).toEqual([]);
    });

    test("should return empty array if there is no metadata", () => {
      const metadataFilter = new MetadataFilterList([]);

      metadataFilter.commit();

      expect(metadataFilter.filteredCategories).toEqual([]);
    });

    test("should return the categories with selected options", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      find(metadataFilter, "split").completeMetadata(["test", "train"]);

      metadataFilter.commit();

      expect(metadataFilter.filteredCategories.map((f) => f.name)).toEqual([
        "split",
      ]);
    });
  });

  describe("hasChangesSinceLatestCommit", () => {
    test("should return true if there is changes", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      find(metadataFilter, "split").completeMetadata(["test", "train"]);

      expect(metadataFilter.hasChangesSinceLatestCommit).toBeTruthy();
    });

    test("should return false if there is no changes", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      expect(metadataFilter.hasChangesSinceLatestCommit).toBeFalsy();
    });
  });

  describe("commit", () => {
    test("should return selected metadata for terms", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      find(metadataFilter, "split").completeMetadata(["test", "train"]);

      const committedFilters = metadataFilter.commit();

      expect(committedFilters).toEqual([
        { name: "split", value: ["test", "train"] },
      ]);
    });

    test("should return the router params for answered filters for numbers", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      find(metadataFilter, "loss").completeMetadata({ ge: 10, le: 20 });

      const committedFilters = metadataFilter.commit();

      expect(committedFilters).toEqual([
        { name: "loss", value: { ge: 10, le: 20 } },
      ]);
    });

    test("should return the router params for answered filters", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      const committedFilters = metadataFilter.commit();

      expect(committedFilters).toEqual([]);
    });
  });

  describe("complete", () => {
    test("should complete the metadata filter by route params", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.complete([
        {
          name: "split",
          value: ["test", "train"],
        },
        {
          name: "loss",
          value: {
            ge: 10,
            le: 20,
          },
        },
        {
          name: "float",
          value: {
            ge: 0.5,
            le: 0.6,
          },
        },
      ]);

      expect(
        find(metadataFilter, "split").selectedOptions.map(
          (option) => option.value
        )
      ).toEqual(["test", "train"]);

      expect(find(metadataFilter, "loss").rangeValue).toEqual({
        ge: 10,
        le: 20,
      });
      expect(find(metadataFilter, "float").rangeValue).toEqual({
        ge: 0.5,
        le: 0.6,
      });
    });

    test("should not support duplicated filtered categories", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.complete([{ name: "split", value: ["test", "train"] }]);

      metadataFilter.complete([{ name: "split", value: ["test", "train"] }]);

      expect(metadataFilter.filteredCategories.map((f) => f.name)).toEqual([
        "split",
      ]);
    });

    test("the user can see the filtered categories in the same order that he/she selected", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.complete([
        { name: "split", value: ["test", "train"] },
        { name: "loss", value: { ge: 10, le: 20 } },
        { name: "float", value: { ge: 0.5, le: 0.6 } },
      ]);

      expect(metadataFilter.filteredCategories.map((f) => f.name)).toEqual([
        "split",
        "loss",
        "float",
      ]);
    });

    test("no modify anything when the param does not contain the option", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.complete([]);

      expect(
        find(metadataFilter, "split").selectedOptions.map(
          (option) => option.value
        )
      ).toEqual([]);
    });

    test("no modify anything when the meta does not exist", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.complete([{ name: "not-exist", value: ["any-value"] }]);

      expect(metadataFilter.filteredCategories).toEqual([]);
    });
  });

  describe("Has Filters", () => {
    test("should return true if there is filters", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      metadataFilter.complete([
        { name: "split", value: ["test", "train"] },
        {
          name: "loss",
          value: {
            ge: 10,
            le: 20,
          },
        },
      ]);

      expect(metadataFilter.hasFilters).toBeTruthy();
    });

    test("should return false if there is no filters", () => {
      const metadataFilter = new MetadataFilterList([]);

      expect(metadataFilter.hasFilters).toBeFalsy();
    });
  });

  describe("complete metadata", () => {
    test("should complete the metadata when is terms", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = find(metadataFilter, "split");

      metadata.completeMetadata(["test", "train"]);

      expect(metadata.selectedOptions.map((option) => option.value)).toEqual([
        "test",
        "train",
      ]);
    });
    test("should complete the metadata when is integer", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = find(metadataFilter, "loss");

      metadata.completeMetadata({ ge: 10, le: 20 });

      expect(metadata.rangeValue).toEqual({ ge: 10, le: 20 });
    });
  });

  describe("Clear", () => {
    test("should clear the metadata when is terms", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = find(metadataFilter, "split");

      metadata.clear();

      expect(metadata.selectedOptions.map((option) => option.value)).toEqual(
        []
      );
    });

    test("should clear the metadata when is integer set the settings max and min values", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());
      const metadata = find(metadataFilter, "loss");
      metadata.completeMetadata({ ge: 10, le: 20 });
      metadata.clear();

      expect(metadata.rangeValue).toEqual({ ge: 0, le: 2 });
    });
  });

  describe("Can Filter", () => {
    test("should return true if the metadata has values", () => {
      const metadataFilter = new MetadataFilterList(createMetadataMock());

      const metadata = find(metadataFilter, "split");

      expect(metadata.canFilter).toBeTruthy();
    });

    test("should return false if terms metadata has no values", () => {
      const metadataFilter = new MetadataFilterList(
        createMetadataWithNoValuesMock()
      );
      const metadata = find(metadataFilter, "split");

      expect(metadata.canFilter).toBeFalsy();
    });

    test("should return false if integer metadata has no values", () => {
      const metadataFilter = new MetadataFilterList(
        createMetadataWithNoValuesMock()
      );
      const metadata = find(metadataFilter, "loss");

      expect(metadata.canFilter).toBeFalsy();
    });

    test("should return false if float metadata has no values", () => {
      const metadataFilter = new MetadataFilterList(
        createMetadataWithNoValuesMock()
      );
      const metadata = find(metadataFilter, "float");

      expect(metadata.canFilter).toBeFalsy();
    });
  });
});
