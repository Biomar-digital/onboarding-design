import type { InfoPanelGroup } from "./types";
import { PLATFORMS_ACCESSES_URL, POND_URL, POND_TUTORIALS_URL } from "./tools";

// The persistent reference panel — always available on the employee side so a
// new designer never has to dig for the essentials mid-task.
export const infoPanel: InfoPanelGroup[] = [
  {
    id: "naming",
    title: "File naming",
    icon: "🗂️",
    rows: [
      {
        label: "Design files",
        value: "Year-Month Language_Market Brand/Product-FileType",
        hint: "File type: Brochure, Ad, Datasheet, Video, etc.",
      },
      {
        label: "Example",
        value: "2022-03 ES_Orbit_Brochure",
        hint: "or DRAFT_2021-03 EN_EMEA SmartCare FOCUS (Marine) DM",
      },
      {
        label: "Images",
        value: "What it is (species, lifestage, location, action…) + license / Shutterstock number / picture default name",
        hint: "Trout_Smolt_Denmark_shutterstock_98966114",
      },
      {
        label: "Videos",
        value: "What it is (species, lifestage, location, action…) + license / Shutterstock number / picture default name",
        hint: "Fish_Tilapia_Grower_shutterstock_25969904",
      },
    ],
  },
  {
    id: "platforms",
    title: "Platforms",
    icon: "🧰",
    rows: [
      { label: "Accesses & lists", value: "Loop Link", url: PLATFORMS_ACCESSES_URL },
      { label: "Brand assets (DAM)", value: "The Pond (Kontainer)", url: POND_URL },
      { label: "The Pond tutorials", value: "Step-by-step how-tos", url: POND_TUTORIALS_URL },
      { label: "Website content", value: "Umbraco" },
      { label: "Stock", value: "Adobe Stock · Shutterstock · Flaticon" },
    ],
  },
];
