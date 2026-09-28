import type { FolderNode } from "./types";

// ─────────────────────────────────────────────────────────────────────────────
// The real Design Hub folder tree (The Pond / Kontainer), transcribed from the
// "Folder Map" Figma board (a top-down org-chart diagram of the shared drive).
// Powers the interactive folder explorer + search (see FolderExplorer.tsx).
// `note` fields come from the small annotation callouts on the original diagram.
// Note: the source diagram has two separate branches both labeled "SALMON" —
// that duplication is preserved here on purpose (see FolderExplorer's index-based
// keys, which handle same-named siblings safely).
// ─────────────────────────────────────────────────────────────────────────────
export const folderTree: FolderNode[] = [
  {
    name: "Design Hub 2.0",
    children: [
      { name: "00. Digital Hub (SoMe)", note: "Illustrative projects we collaborate with Digital Hub (Website, SoMe, customer portal, etc.)",
        children: [
          { name: "Digital Project", note: "Mostly website assets. Made to also share other digital projects such as customer portal.",
            children: [
              { name: "¤ Website Assets",
                children: [
                  { name: "00. Home" },
                  { name: "01. Feed and Services" },
                  { name: "02. Our Promise" },
                  { name: "03. Better Feed" },
                  { name: "04. Our Story" },
                  { name: "05. Insights" }
                ]
              },
              { name: "Bags", note: "Here you can add the bag mock-ups that go into the website. Just follow the product segmentation.",
                children: [
                  { name: "EDITABLE",
                    children: [
                      { name: "Archive" },
                      { name: "Broodstock" },
                      { name: "CN Bags" },
                      { name: "EXIA" },
                      { name: "Finisher" },
                      { name: "First Feeding" },
                      { name: "Health" },
                      { name: "High Performance" },
                      { name: "Organic" },
                      { name: "RAS" },
                      { name: "Shrimp" },
                      { name: "Smoltification" },
                      { name: "Standard Performance" },
                      { name: "Sustainability" },
                      { name: "Top Performance" },
                      { name: "VN Bags" }
                    ]
                  }
                ]
              },
              { name: "Costumer Portal" },
              { name: "Error Pages" }
            ]
          },
          { name: "Real fishy facts - Assets" },
          { name: "Some posts 2026" },
          { name: "SoMe posts Previous years",
            children: [
              { name: "2023" },
              { name: "2024" },
              { name: "2025" }
            ]
          },
          { name: "¤ BioMar Logos", note: "All approved BioMar logos.",
            children: [
              { name: "1. BioMar Primary - Corporate Logo" },
              { name: "BioMar Logo - Social Media Circle" },
              { name: "BioMar Logo Animation" },
              { name: "BioMar Logo Element - without..." },
              { name: "BioMar Logo with Tagline" },
              { name: "BioMar Logo without box" },
              { name: "BioMar Solid Blue Logo" },
              { name: "BioMar Solid White Logo" },
              { name: "BioMar Tagline" },
              { name: "Black & White Logo" },
              { name: "EXT BioMar Brand Package - Web" },
              { name: "EXT BioMar Logo Package" },
              { name: "Old BioMar logo" }
            ]
          },
          { name: "10. Product Logos (unclear)", note: "Product and sub-product logos. Sub-products can be found at the specific product folder. E.g. EFICO Alpha logo inside EFICO Logo folder.",
            children: [
              { name: "¤ Archive" },
              { name: "AquaVet Logo" },
              { name: "BioFarm Logo" },
              { name: "BioSustain Logo" },
              { name: "BioSustain MASTERCLASS L..." },
              { name: "Blue Impact Logo" },
              { name: "CPK Logo" },
              { name: "DAN-EK Logo" },
              { name: "ECOLIFE Logo" },
              { name: "EFICO Logo" },
              { name: "ENERGY Logo" },
              { name: "EXIA Logo" },
              { name: "GOLDEN REPRODUCTOR L..." },
              { name: "INICIO Logos" },
              { name: "INICIO Shrimp Logo" },
              { name: "INTRO Logo" },
              { name: "LARVIVA Logos" },
              { name: "Maxio Logo" },
              { name: "ORBIT Logo" },
              { name: "POWER Logo" },
              { name: "SmartCare Logos" },
              { name: "Symbio Logo" },
              { name: "TRI-X Logo" },
              { name: "VetCare Logo" }
            ]
          }
        ]
      },
      { name: "0. Design Assets" },
      { name: "1. SmartCare",
        children: [
          { name: "¤ 1. SmartCare Logos", note: "Product and sub-product logos. Print and digital logos." },
          { name: "¤ Adverts", note: "General SmartCare Ads" },
          { name: "¤ General", note: "Other General SmartCare Materials" },
          { name: "¤ Roll-Up Banners" },
          { name: "¤ Salmon Illustration", note: "Scientific Salmon Illustration" },
          { name: "Sub-Product Folders", note: "The Sub-Product Folders can have specific material for there: Ads, Sales, Campaign, Banners, etc.  If you can't find a folder for a specific Sub-Product, please create and start building it!" }
        ]
      },
      { name: "2. LARVIVA",
        children: [
          { name: "1. LARVIVA Logo", note: "Product and sub-product logos. Print and digital logos." },
          { name: "2. Hatchery Pictures", note: "Photoshoots made of hatchery" },
          { name: "3. LARVIVA Video", note: "All assets and project (As of 27 July 2026, product video is not ready)" },
          { name: "4. Hatchery Product Training Certificates", note: "2022 Certificates (if they're to be used again, they need new logo update)" },
          { name: "5. Merchandise", note: "LARVIVA Merch (needs to be checked before being used again, in case it has the old logo)" },
          { name: "6. Guidelines", note: "Currently DRAFT version. Learn more in the Product Brand Guidelines" },
          { name: "7. Events" },
          { name: "Adverts_Generic", note: "Folder for generic ads. Not usual, as they're usually advertised as FISH or SHRIMP separately" },
          { name: "Email Signature Banner" },
          { name: "Hatchery Infographic", note: "Life stage graph" },
          { name: "LARVIVA HUB", note: "Assets for the space in the Hirtshals ATC" },
          { name: "0. FISH", note: "Folder specific for Fish LARVIVA",
            children: [
              { name: "¤ LARVIVA ORBIT", note: "Folder specific for LARVIVA ORBIT material" },
              { name: "Packaging Pictures" },
              { name: "Adverts" },
              { name: "Assets", note: "Artwork specific to LARVIVA fish" },
              { name: "Brochures" },
              { name: "Datasheets" },
              { name: "ESB", note: "Email Signature Banners (ESB)" },
              { name: "Labels" },
              { name: "Merchandise" },
              { name: "Overviews" },
              { name: "Presentations" }
            ]
          },
          { name: "0. SHRIMP", note: "Folder specific for Shrimp LARVIVA",
            children: [
              { name: "¤ Assets & Images", note: "Artwork specific to LARVIVA SHRIMP" },
              { name: "Adverts" },
              { name: "Brochures" },
              { name: "Datasheets" },
              { name: "ESB", note: "Email Signature Banners (ESB)" },
              { name: "Labels" },
              { name: "Merch" },
              { name: "Packaging Pictures" },
              { name: "PPT" },
              { name: "Roll Ups" },
              { name: "Videos" }
            ]
          }
        ]
      },
      { name: "3. ORBIT",
        children: [
          { name: "1. ORBIT Logo", note: "Product and sub-product logos. Print and digital logos." },
          { name: "Adverts", note: "General ORBIT Ads" },
          { name: "Brochures", note: "General ORBIT brochures" },
          { name: "Datasheets" },
          { name: "Merch" },
          { name: "Presentations" },
          { name: "SoMe" },
          { name: "PPT" },
          { name: "Roll Ups" },
          { name: "Videos" }
        ]
      },
      { name: "4. EXIA",
        children: [
          { name: "□ Archive" },
          { name: "1. EXIA Logo", note: "Product and sub-product logos. Print and digital logos." },
          { name: "ACTIVA", note: "Sub-product files" },
          { name: "ECOLIFE", note: "Sub-product files" },
          { name: "FOCUS", note: "Sub-product files" },
          { name: "MAXIO", note: "Sub-product files" },
          { name: "MAXIO BOOST", note: "Sub-product files" },
          { name: "PERFORM", note: "Sub-product files" },
          { name: "PRIME", note: "Sub-product files" },
          { name: "PRO", note: "Sub-product files" },
          { name: "START", note: "Sub-product files" },
          { name: "□ EXIA Range", note: "General EXIA material",
            children: [
              { name: "Adverts" },
              { name: "Brochures" },
              { name: "CN_Feed Bag" },
              { name: "Datasheets" },
              { name: "Feed samples" },
              { name: "Merch" },
              { name: "Poster" },
              { name: "Roll up" },
              { name: "SoMe" }
            ]
          },
          { name: "VN_Celestial Harmony Line", note: "Customer-specific line in Vietnam",
            children: [
              { name: "ACTIVA COMET" },
              { name: "PERFORM NOVA" },
              { name: "PRIME STAR" }
            ]
          }
        ]
      },
      { name: "5. Blue Impact",
        children: [
          { name: "¤ Blue Impact Video", note: "Product Video" },
          { name: "¤ Campaigns", note: "Campaigns made by markets" },
          { name: "¤ Logo" },
          { name: "Adverts" },
          { name: "Assets" },
          { name: "Billboards" },
          { name: "Brochures" },
          { name: "Merchandise" },
          { name: "PPTs" }
        ]
      },
      { name: "6. INICIO and INTRO",
        children: [
          { name: "INICIO FISH",
            children: [
              { name: "□ Adverts", note: "General INICIO FISH Ads" },
              { name: "□ Assets" },
              { name: "□ Logos" },
              { name: "□ Packaging Pictures" },
              { name: "Brochures" },
              { name: "Documentation Material" },
              { name: "INICIO Akai", note: "Sub-product files" },
              { name: "INICIO Plus", note: "Sub-product files" },
              { name: "INICIO Plus M", note: "Sub-product files" },
              { name: "INICIO Plus S", note: "Sub-product files" },
              { name: "INICIO Quinnat", note: "Sub-product files" },
              { name: "INICIO Rainbow", note: "Sub-product files" }
            ]
          },
          { name: "INICIO Shrimp",
            children: [
              { name: "□ INICIO Range", note: "General INICIO SHRIMP Material" },
              { name: "□ Logos" },
              { name: "INICIO Focus", note: "Sub-product files" },
              { name: "INICIO Maxio", note: "Sub-product files" },
              { name: "INICIO Plus", note: "Sub-product files" },
              { name: "INICIO Prime", note: "Sub-product files" },
              { name: "INICIO Pro", note: "Sub-product files" },
              { name: "VN_Boxes_10kg", note: "General INICIO Box for Vietnam market" }
            ]
          },
          { name: "INTRO",
            children: [
              { name: "□ Logos", note: "Product and sub-product logos. Print and digital logos." },
              { name: "INTRO Plus MT", note: "Sub-product files" },
              { name: "INTRO Q", note: "Sub-product files" },
              { name: "INTRO Q+", note: "Sub-product files" },
              { name: "Presentations" },
              { name: "Videos" }
            ]
          }
        ]
      },
      { name: "7. EFICO, MAXIO and POWER",
        children: [
          { name: "□ Brochures", note: "General Grower Brochures" },
          { name: "Assets" },
          { name: "EFICO",
            children: [
              { name: "□ EFICO Range", note: "General EFICO Material" },
              { name: "□ EFICO Logos", note: "Product and sub-product logos. Print and digital logos." },
              { name: "□ Feed Bags", note: "Feedbags for specific markets" },
              { name: "EFICO Alpha 717", note: "Sub-product files" },
              { name: "EFICO Alpha 790", note: "Sub-product files" },
              { name: "EFICO Alpha 790FT", note: "Sub-product files" },
              { name: "EFICO Enviro 920 Advance", note: "Sub-product files" },
              { name: "EFICO Enviro 923 Advance", note: "Sub-product files" },
              { name: "EFICO Genio 991", note: "Sub-product files" },
              { name: "Video", note: "At least for now, not a finished project" }
            ]
          },
          { name: "MAXIO",
            children: [
              { name: "□ Logos", note: "Product and sub-product logos. Print and digital logos." },
              { name: "□ MAXIO Range", note: "General MAXIO Material" },
              { name: "Maxio Barra", note: "Sub-product files" }
            ]
          },
          { name: "POWER",
            children: [
              { name: "□ POWER Logos", note: "Product and sub-product logos. Print and digital logos." },
              { name: "□ POWER Range", note: "General MAXIO Material" },
              { name: "H2O", note: "Sub-product files" }
            ]
          }
        ]
      },
      { name: "8. BioFarm",
        children: [
          { name: "¤ BioFarm Logo", note: "All logo versions. Print and digital logos." },
          { name: "¤ BioFarm Manual", note: "Manuals adapted for different markets" },
          { name: "¤ Other BioFarm Logos", note: "Logos of BioFarm programmes, such as BioFarm Academy and BioFarm Online" },
          { name: "Document Templates" },
          { name: "ESB" },
          { name: "Icons" },
          { name: "Merch" },
          { name: "Photos" },
          { name: "PPT" },
          { name: "Videos" }
        ]
      },
      { name: "ASIA",
        children: [
          { name: "China",
            children: [
              { name: "□ Archive" },
              { name: "□ Billboards" },
              { name: "□ BioFarm pic" },
              { name: "□ Brochures" },
              { name: "□ Corporate", note: "Material for Corporate" },
              { name: "□ Factory_Office_Signage_Stationary", note: "Material for Factory" },
              { name: "□ Feed Bags", note: "Customized Product Bags" },
              { name: "□ Handouts" },
              { name: "□ Labels" },
              { name: "□ Logos", note: "JV logos" },
              { name: "□ Uniforms" },
              { name: "Icons",
                children: [
                  { name: "Fish" },
                  { name: "Gems" }
                ]
              },
              { name: "Images" },
              { name: "Slides" },
              { name: "Storefronts" },
              { name: "Tech Centre Video-Subtitles" }
            ]
          },
          { name: "Vietnam",
            children: [
              { name: "Archive" },
              { name: "Assets" },
              { name: "Business Cards" },
              { name: "Conferences & Expos", note: "Material created for conferences and expos such as booths" },
              { name: "Corporate", note: "Material for Corporate" },
              { name: "Office", note: "Material for Office" },
              { name: "0. BioMar Viet Uc Guidelines" },
              { name: "1. BioMar Viet Uc Logo" },
              { name: "2. Factory_Signage_Office" },
              { name: "ACTIVA", note: "Product exclusive for Vietnam market" },
              { name: "Leaflet" },
              { name: "Merch" },
              { name: "Photo" },
              { name: "Signboards" },
              { name: "SoMe" },
              { name: "Visitor card" }
            ]
          }
        ]
      },
      { name: "CORPORATE",
        children: [
          { name: "Archive" },
          { name: "Business Cards", note: "Business Cards for BioMar Group" },
          { name: "Global Policies" },
          { name: "Aarhus Office", note: "Aarhus office \"decor\"" },
          { name: "2025-10 Biomar corporate video" },
          { name: "2025-01 BioMar Value Chain (unclear)" },
          { name: "Finance" },
          { name: "GDPR" },
          { name: "Health and Safety" },
          { name: "HR" },
          { name: "IT" },
          { name: "Manufacturing" },
          { name: "Sourcing" }
        ]
      },
      { name: "EMEA",
        children: [
          { name: "¤ Archive" },
          { name: "¤ Brochures" },
          { name: "¤ Business Cards", note: "Business Cards for EMEA Markets" },
          { name: "¤ Calendars", note: "Every year Wall Planners and Agendas for employees" },
          { name: "¤ Conferences & Expos", note: "Material created for conferences and expos such as booths" },
          { name: "¤ Datasheets", note: "Product Datasheets" },
          { name: "¤ Factory_Office_Signage" },
          { name: "¤ Feed Catalogues", note: "Every year Feed Catalogues tailored per market" },
          { name: "¤ Feed Overviews", note: "Every year Feed overview tailored per specie and market" },
          { name: "¤ Handbooks" },
          { name: "¤ Lanyard ID Card" },
          { name: "¤ Posters", note: "Information Posters tailored in different languages" },
          { name: "¤ PPT_Presentations" },
          { name: "¤ Videos" },
          { name: "5. DAN EX", note: "Product exclusive for EMEA Markets" },
          { name: "SoMe" },
          { name: "¤ BioMar Sagun", note: "Folder specific for the JV Company in Turkey",
            children: [
              { name: "¤ Archive" },
              { name: "¤ Brochures" },
              { name: "¤ Calendars", note: "Every year Calendars for employees" },
              { name: "1. BioMar Sagun Logo", note: "All approved logos. Print and digital" },
              { name: "2. Business Cards" },
              { name: "3. Feed Bag" },
              { name: "4. Factory" },
              { name: "BioMar Sagun ESB" },
              { name: "BioMar Sagun Lanyard" },
              { name: "BioMar Sagun Notebooks" },
              { name: "BioMar Sagun Staff Photos" },
              { name: "SoMe" }
            ]
          }
        ]
      },
      { name: "GLOBAL", note: "Everything related to Global Marketing, meaning our team and things used globally",
        children: [
          { name: "□ Archive",
            children: [
              { name: "□ BioRetain" },
              { name: "□ Brochures", note: "General BioMar Brochures" },
              { name: "□ Merch" },
              { name: "3. Christmas" },
              { name: "4. Press Releases" },
              { name: "BioMar Corporate Video" },
              { name: "BioMar Tech Centre Video" },
              { name: "BioMar Technology Video" },
              { name: "Office Design Inspo", note: "Offices around the world images. Every now and then needs to be updated" },
              { name: "Screensaver & Desktop" }
            ]
          },
          { name: "□ Design Hub",
            children: [
              { name: "Design hub onboarding" },
              { name: "Design Hub Process", note: "Process to show new marketing managers or other collaborators" },
              { name: "Design Hub Task Report", note: "Report to do every end of the year on how many tasks we did" },
              { name: "Digital BCs project" },
              { name: "Global policies platform" },
              { name: "The hub minute format" }
            ]
          },
          { name: "1. Campaigns",
            children: [
              { name: "□ Archived Campaigns" },
              { name: "Better Feed. Better Fish. Better Food. Campaign (BFBF)" },
              { name: "Better Feed. Better Food. Campaign (BFBF)" },
              { name: "BioMar Farmers Campaign (BFC)" },
              { name: "Fish health videos 101" },
              { name: "Grower Campaign (GC)" },
              { name: "Our Promise Campaign (OPC)" },
              { name: "Our Purpose Campaign (PRC)" },
              { name: "Sustainable Nutrition Campaign (SNC)" },
              { name: "The Swoosh",
                children: [
                  { name: "We Are BioMar Campaign (WBC)" }
                ]
              }
            ]
          }
        ]
      },
      { name: "LATAM",
        children: [
          { name: "Costa Rica (CR)",
            children: [
              { name: "¤ Business Cards" },
              { name: "¤ Conferences & Expos" },
              { name: "1. Corporate" },
              { name: "Adverts" },
              { name: "Agendas" },
              { name: "Feed Bags" },
              { name: "Invitations" },
              { name: "Merch" }
            ]
          },
          { name: "Ecuador (EC)",
            children: [
              { name: "1. Pictures" },
              { name: "2. Videos" },
              { name: "Advertisements" },
              { name: "Archive" },
              { name: "Business Cards" },
              { name: "Calendars" },
              { name: "Conferences & Expos" },
              { name: "Feed Overviews" },
              { name: "Handouts" },
              { name: "Invitations" },
              { name: "Posters" },
              { name: "Product Samples" },
              { name: "Social Media" },
              { name: "Technical-Commercial Asset Guide" }
            ]
          }
        ]
      },
      { name: "SALMON",
        children: [
          { name: "Australia (AUS)",
            children: [
              { name: "Archive" },
              { name: "Business Cards" },
              { name: "ECOline", note: "...ol (unclear, cut off at image edge)" },
              { name: "Factory_Signage_Office" },
              { name: "Merch" },
              { name: "SoMe" }
            ]
          },
          { name: "Chile (CL)",
            children: [
              { name: "Adverts" },
              { name: "Archive" },
              { name: "Billboards" },
              { name: "Business Cards" },
              { name: "Campaigns" },
              { name: "Conferences & Expos" },
              { name: "Feed Bags" },
              { name: "Flags" },
              { name: "Merch" },
              { name: "Office" },
              { name: "Posters" },
              { name: "Photo Guidelines" }
            ]
          },
          { name: "Iceland (IS)",
            children: [
              { name: "Conferences & Expos" }
            ]
          },
          { name: "Norway (NO)",
            children: [
              { name: "Archive" },
              { name: "Big Bags" },
              { name: "Business Cards" },
              { name: "Conferences" },
              { name: "Posters" },
              { name: "Adverts" },
              { name: "Banners" },
              { name: "Billboards" },
              { name: "FÖROPPLYSNINGEN" },
              { name: "Kvarøy Handout" },
              { name: "Merch" },
              { name: "Myre Office" },
              { name: "NO Portraits" },
              { name: "NO_Videos" },
              { name: "Roll-Up Banners" },
              { name: "SoMe" },
              { name: "SoMe_Winter Feed Strategy" }
            ]
          },
          { name: "Scotland (UK)",
            children: [
              { name: "Archive" },
              { name: "Business Cards" },
              { name: "Conferences" },
              { name: "Adverts" },
              { name: "Merch" },
              { name: "Office Design_Grangemouth" },
              { name: "Truck" }
            ]
          },
          { name: "SYMBIO", note: "Product exclusive for SALMON Markets" },
          { name: "¤ Tri X", note: "Product exclusive for SALMON Markets" }
        ]
      },
      { name: "RnD" },
      { name: "SALMON",
        children: [
          { name: "¤ Archive" },
          { name: "1. Sustainability Report" },
          { name: "2. BioSustain" },
          { name: "3. BioSustain Masterclass" },
          { name: "4. White Papers" },
          { name: "Auchan Shrimp Video" },
          { name: "Discover Tool" },
          { name: "EN_Our Ambition Videos" },
          { name: "PPTs" }
        ]
      }
    ],
  },
];
