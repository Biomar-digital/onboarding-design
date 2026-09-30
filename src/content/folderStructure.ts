import type { FolderNode } from "./types";

// ─────────────────────────────────────────────────────────────────────────────
// The real Design Hub folder tree (The Pond / Kontainer), transcribed from the
// "Folder Map" Figma board (a top-down org-chart diagram of the shared drive).
// Powers the interactive folder explorer + search (see FolderExplorer.tsx).
// Every folder carries a `note`: some are the original annotation callouts from
// the source diagram, the rest are inferred from the folder's name and place in
// the tree so every folder has a short explanation, not just the annotated ones.
// Note: the source diagram has two separate branches both labeled "SALMON" —
// that duplication is preserved here on purpose (see FolderExplorer's index-based
// keys, which handle same-named siblings safely).
// ─────────────────────────────────────────────────────────────────────────────
export const folderTree: FolderNode[] = [
  {
    name: "Design Hub 2.0",
    note: "The Design Hub's shared drive (The Pond / Kontainer), root of everything below.",
    children: [
      { name: "00. Digital Hub (SoMe)", note: "Illustrative projects we collaborate with Digital Hub (Website, SoMe, customer portal, etc.)",
        children: [
          { name: "Digital Project", note: "Mostly website assets. Made to also share other digital projects such as customer portal.",
            children: [
              { name: "¤ Website Assets", note: "Image and graphic assets organized by website page/section",
                children: [
                  { name: "00. Home", note: "Assets for the website Home page" },
                  { name: "01. Feed and Services", note: "Assets for the website Feed and Services page" },
                  { name: "02. Our Promise", note: "Assets for the website Our Promise page" },
                  { name: "03. Better Feed", note: "Assets for the website Better Feed page" },
                  { name: "04. Our Story", note: "Assets for the website Our Story page" },
                  { name: "05. Insights", note: "Assets for the website Insights page" }
                ]
              },
              { name: "Bags", note: "Here you can add the bag mock-ups that go into the website. Just follow the product segmentation.",
                children: [
                  { name: "EDITABLE", note: "Editable bag mock-up source files by product segment",
                    children: [
                      { name: "Archive", note: "Old/discontinued bag mock-up files" },
                      { name: "Broodstock", note: "Bag mock-ups for Broodstock products" },
                      { name: "CN Bags", note: "Bag mock-ups for the China market" },
                      { name: "EXIA", note: "Bag mock-ups for the EXIA product line" },
                      { name: "Finisher", note: "Bag mock-ups for Finisher products" },
                      { name: "First Feeding", note: "Bag mock-ups for First Feeding products" },
                      { name: "Health", note: "Bag mock-ups for Health products" },
                      { name: "High Performance", note: "Bag mock-ups for High Performance products" },
                      { name: "Organic", note: "Bag mock-ups for Organic products" },
                      { name: "RAS", note: "Bag mock-ups for RAS (Recirculating Aquaculture System) products" },
                      { name: "Shrimp", note: "Bag mock-ups for Shrimp products" },
                      { name: "Smoltification", note: "Bag mock-ups for Smoltification products" },
                      { name: "Standard Performance", note: "Bag mock-ups for Standard Performance products" },
                      { name: "Sustainability", note: "Bag mock-ups for Sustainability products" },
                      { name: "Top Performance", note: "Bag mock-ups for Top Performance products" },
                      { name: "VN Bags", note: "Bag mock-ups for the Vietnam market" }
                    ]
                  }
                ]
              },
              { name: "Costumer Portal", note: "Assets for the customer portal digital project" },
              { name: "Error Pages", note: "Website error page assets (e.g. 404)" }
            ]
          },
          { name: "Real fishy facts - Assets", note: "Assets for the 'Real fishy facts' social media content series" },
          { name: "Some posts 2026", note: "Social media posts for 2026" },
          { name: "SoMe posts Previous years", note: "Archived social media posts from earlier years",
            children: [
              { name: "2023", note: "Archived SoMe posts from 2023" },
              { name: "2024", note: "Archived SoMe posts from 2024" },
              { name: "2025", note: "Archived SoMe posts from 2025" }
            ]
          },
          { name: "¤ BioMar Logos", note: "All approved BioMar logos.",
            children: [
              { name: "1. BioMar Primary - Corporate Logo", note: "Main BioMar corporate logo files" },
              { name: "BioMar Logo - Social Media Circle", note: "BioMar logo formatted for social media profile circles" },
              { name: "BioMar Logo Animation", note: "Animated version of the BioMar logo" },
              { name: "BioMar Logo Element - without...", note: "BioMar logo element variant without extra graphic elements" },
              { name: "BioMar Logo with Tagline", note: "BioMar logo including the company tagline" },
              { name: "BioMar Logo without box", note: "BioMar logo without the surrounding box" },
              { name: "BioMar Solid Blue Logo", note: "Solid blue version of the BioMar logo" },
              { name: "BioMar Solid White Logo", note: "Solid white version of the BioMar logo" },
              { name: "BioMar Tagline", note: "BioMar tagline graphic files" },
              { name: "Black & White Logo", note: "Black and white version of the BioMar logo" },
              { name: "EXT BioMar Brand Package - Web", note: "External-facing BioMar brand package for web use" },
              { name: "EXT BioMar Logo Package", note: "External-facing BioMar logo package for partners/third parties" },
              { name: "Old BioMar logo", note: "Previous/retired version of the BioMar logo" }
            ]
          },
          { name: "10. Product Logos (unclear)", note: "Product and sub-product logos. Sub-products can be found at the specific product folder. E.g. EFICO Alpha logo inside EFICO Logo folder.",
            children: [
              { name: "¤ Archive", note: "Archived/outdated product logo files" },
              { name: "AquaVet Logo", note: "AquaVet product logo files" },
              { name: "BioFarm Logo", note: "BioFarm product logo files" },
              { name: "BioSustain Logo", note: "BioSustain product logo files" },
              { name: "BioSustain MASTERCLASS L...", note: "BioSustain Masterclass product logo files" },
              { name: "Blue Impact Logo", note: "Blue Impact product logo files" },
              { name: "CPK Logo", note: "CPK product logo files" },
              { name: "DAN-EK Logo", note: "DAN-EK product logo files" },
              { name: "ECOLIFE Logo", note: "ECOLIFE product logo files" },
              { name: "EFICO Logo", note: "EFICO product logo files" },
              { name: "ENERGY Logo", note: "ENERGY product logo files" },
              { name: "EXIA Logo", note: "EXIA product logo files" },
              { name: "GOLDEN REPRODUCTOR L...", note: "GOLDEN REPRODUCTOR product logo files" },
              { name: "INICIO Logos", note: "INICIO product logo files" },
              { name: "INICIO Shrimp Logo", note: "INICIO Shrimp product logo files" },
              { name: "INTRO Logo", note: "INTRO product logo files" },
              { name: "LARVIVA Logos", note: "LARVIVA product logo files" },
              { name: "Maxio Logo", note: "Maxio product logo files" },
              { name: "ORBIT Logo", note: "ORBIT product logo files" },
              { name: "POWER Logo", note: "POWER product logo files" },
              { name: "SmartCare Logos", note: "SmartCare product logo files" },
              { name: "Symbio Logo", note: "Symbio product logo files" },
              { name: "TRI-X Logo", note: "TRI-X product logo files" },
              { name: "VetCare Logo", note: "VetCare product logo files" }
            ]
          }
        ]
      },
      { name: "0. Design Assets", note: "Brand-wide design assets shared across all products: logos, guidelines, templates and media libraries",
        children: [
          { name: "¤ BioMar Logos", note: "All approved BioMar logos.",
            children: [
              { name: "1. BioMar Primary - Corporate Logo", note: "The main corporate version of the BioMar logo" },
              { name: "BioMar Logo - Social Media Circle", note: "The circular version of the BioMar logo for social media" },
              { name: "BioMar Logo Animation", note: "The animated version of the BioMar logo" },
              { name: "BioMar Logo Element - without Wordmark", note: "The logo mark version of the BioMar logo, without the wordmark" },
              { name: "BioMar Logo with Tagline", note: "The version of the BioMar logo that includes the tagline" },
              { name: "BioMar Logo without box", note: "The version of the BioMar logo without its surrounding box" },
              { name: "BioMar Solid Blue Logo", note: "The solid blue version of the BioMar logo" },
              { name: "BioMar Solid White Logo", note: "The solid white version of the BioMar logo" },
              { name: "BioMar Tagline", note: "The BioMar tagline on its own, for use apart from the full logo" },
              { name: "Black & White Logo", note: "The black & white version of the BioMar logo" },
              { name: "EXT BioMar Brand Package - Web", note: "External-facing BioMar brand package for web use" },
              { name: "EXT BioMar Logo Package", note: "External-facing package of BioMar logo files" },
              { name: "Old BioMar logo", note: "The previous, retired version of the BioMar logo, kept for reference" }
            ]
          },
          { name: "0. Product Logos", note: "Product and sub-product logos. Sub-products can be found on the specific product folder. E.g. EFICO Alpha logo inside EFICO Logo folder",
            children: [
              { name: "¤Archive", note: "Archived, retired product logo files" },
              { name: "AquaVet Logo", note: "Logo files for the AquaVet product line" },
              { name: "BioFarm Logo", note: "Logo files for the BioFarm product line" },
              { name: "BioSustain Logo", note: "Logo files for the BioSustain program" },
              { name: "BioSustain MASTERCLASS L...", note: "Logo files for the BioSustain Masterclass program" },
              { name: "Blue Impact Logo", note: "Logo files for the Blue Impact product line" },
              { name: "CPK Logo", note: "Logo files for the CPK product line" },
              { name: "DAN-EX Logo", note: "Logo files for the DAN-EX product line" },
              { name: "ECOLIFE Logo", note: "Logo files for the ECOLIFE product line" },
              { name: "EFICO Logo", note: "Logo files for the EFICO product line" },
              { name: "ENERGY Logo", note: "Logo files for the ENERGY product line" },
              { name: "EXIA Logo", note: "Logo files for the EXIA product line" },
              { name: "GOLDEN REPRODUCTOR L...", note: "Logo files for the Golden Reproductor product line" },
              { name: "INICIO Logos", note: "Logo files for the INICIO product line" },
              { name: "INICIO Shrimp Logo", note: "Logo files for the INICIO Shrimp product line" },
              { name: "INTRO Logo", note: "Logo files for the INTRO product line" },
              { name: "LARVIVA Logos", note: "Logo files for the LARVIVA product line" }
            ]
          },
          { name: "01. Photo Library", note: "All photos are used or have been done by BioMar. Only Global Marketing has access to this folder.",
            children: [
              { name: "BioMar Facilities", note: "Photos of Production Facilities around the globe" },
              { name: "BioMar Photoshoots", note: "Photoshoot folders organized by location, year and project" },
              { name: "BioMar Staff", note: "Portrait images of Staff around the world, organized by name" },
              { name: "BioMar Transport", note: "Trucks, vessels, etc" },
              { name: "Carlos diaz pictures", note: "Some Carlos images, refer to the most current ones on the \"BioMar Staff\" folder" },
              { name: "Feed - SPECIFIC", note: "Photos of specific BioMar feed products" },
              { name: "Stock Photo Sites", note: "Links to other stock photo sites in case something more specific is needed" },
              { name: "TO EDIT", note: "Photos awaiting editing before being added to the library" },
              { name: "To Organise", note: "Duplicated images or images that need to be localized into a new place" }
            ]
          },
          { name: "02. Video Library", note: "Stock videos and BioMar videos",
            children: [
              { name: "BioMar Videos", note: "Corporate and Product Videos" },
              { name: "2025-10 AQ1 video", note: "AQ1 Corporate video (should be stored in the AQ1 folder though)" },
              { name: "2025-10 Biomar corporate video", note: "BioMar Corporate video (should be stored in CORPORATE folder though)" },
              { name: "R&D Footage - Elisabeth", note: "Fish 101 Videos (should be stored in GLOBAL folder though)" }
            ]
          },
          { name: "03. Audio Library", note: "Sound and music for videos" },
          { name: "04. Asset Library", note: "Various useful assets",
            children: [
              { name: "¤ Life Stages", note: "Salmon life stages illustrations (also available in icon library - all species)" },
              { name: "Flags - Rounded corners", note: "All countries flags we use for presentations, posters, etc." },
              { name: "gems", note: "Used for CN tags." },
              { name: "Hatchery Infographic", note: "Life cycle used in LARVIVA and other communications" },
              { name: "UN SDG Icons", note: "UN Sustainable Development Goals icons in most languages" }
            ]
          },
          { name: "05. JV Logos + Assets", note: "JV Logos + other material (email signature banners, big logos, etc)  Material can also be found in their own folders",
            children: [
              { name: "BioMar Sagun", note: "Can also be found in EMEA > BioMar Sagun." },
              { name: "BioMar Tongwei Logo", note: "Can also be found in ASIA > China." },
              { name: "BioMar Viet Uc Logo", note: "Can also be found in ASIA > Vietnam." }
            ]
          },
          { name: "06. Icon Library", note: "Source icon files and their exported formats, used across BioMar communications",
            children: [
              { name: "2025 Above and Beyond.ai", note: "File to edit the Above and Beyond graph." },
              { name: "All icons.ai", note: "All the BioMar icons we use and make available for people in The Pond later. They're grouped in different categories to find them easily inside the file." },
              { name: "All Icons SVG", note: "SVG exports of all the BioMar icons" },
              { name: "BioMar factories.ai", note: "All BioMar Production Facilities icons." },
              { name: "Factory Icons", note: "Exported factory icon files" },
              { name: "BioMar Detailed Fish Icons_FINAL.ai", note: "All species fed by BioMar + some life stages." },
              { name: "Detailed Fish", note: "Exported detailed fish icon files" },
              { name: "Farming methods_icons.ai", note: "Most farming methods." },
              { name: "Farming Methods", note: "Exported farming methods icon files" },
              { name: "Fish Life Cycle.ai", note: "Used for LARVIVA communications." },
              { name: "Scopes Icons.ai", note: "Used mostly on QSR or GRI booklets to report on emissions." },
              { name: "Scope 1 2 and 3", note: "Exported Scope 1, 2 and 3 icon files" },
              { name: "Swoosh Circle.ai", note: "Different swoosh compositions for graphs." },
              { name: "Impact Parameters", note: "BioSustain Impact Parameters" },
              { name: "Manufacturing Icons", note: "Manufacturing process icons" }
            ]
          },
          { name: "BioMar Brand Guidelines", note: "BioMar's official brand guideline documents",
            children: [
              { name: "BioMar Brand Guidelines 2026", note: "The current version of BioMar's brand guidelines" },
              { name: "BioMar Brand Voice Guideline 2026", note: "The current version of BioMar's brand voice and tone guidelines" },
              { name: "BioMar Product Brand Guidelines...", note: "Brand guidelines specific to BioMar's product lines" },
              { name: "BioMar Service Guidelines 2025", note: "The current version of BioMar's service brand guidelines" },
              { name: "Photoshoot Guidelines 2024", note: "Guidelines for planning and shooting BioMar photoshoots" },
              { name: "Portrait Photo Guidelines 2024", note: "Guidelines for shooting staff portrait photos" }
            ]
          }
        ]
      },
      { name: "1. SmartCare", note: "SmartCare salmon-feed product line design assets.",
        children: [
          { name: "¤ 1. SmartCare Logos", note: "Product and sub-product logos. Print and digital logos." },
          { name: "¤ Adverts", note: "General SmartCare Ads" },
          { name: "¤ General", note: "Other General SmartCare Materials" },
          { name: "¤ Roll-Up Banners", note: "Roll-up banner designs for SmartCare events and trade shows" },
          { name: "¤ Salmon Illustration", note: "Scientific Salmon Illustration" },
          { name: "Sub-Product Folders", note: "The Sub-Product Folders can have specific material for there: Ads, Sales, Campaign, Banners, etc.  If you can't find a folder for a specific Sub-Product, please create and start building it!" }
        ]
      },
      { name: "2. LARVIVA", note: "LARVIVA brand assets for larval fish and shrimp feed, split into Fish and Shrimp lines.",
        children: [
          { name: "1. LARVIVA Logo", note: "Product and sub-product logos. Print and digital logos." },
          { name: "2. Hatchery Pictures", note: "Photoshoots made of hatchery" },
          { name: "3. LARVIVA Video", note: "All assets and project (As of 27 July 2026, product video is not ready)" },
          { name: "4. Hatchery Product Training Certificates", note: "2022 Certificates (if they're to be used again, they need new logo update)" },
          { name: "5. Merchandise", note: "LARVIVA Merch (needs to be checked before being used again, in case it has the old logo)" },
          { name: "6. Guidelines", note: "Currently DRAFT version. Learn more in the Product Brand Guidelines" },
          { name: "7. Events", note: "Materials used for LARVIVA events and trade shows." },
          { name: "Adverts_Generic", note: "Folder for generic ads. Not usual, as they're usually advertised as FISH or SHRIMP separately" },
          { name: "Email Signature Banner", note: "Email signature banner graphics for LARVIVA." },
          { name: "Hatchery Infographic", note: "Life stage graph" },
          { name: "LARVIVA HUB", note: "Assets for the space in the Hirtshals ATC" },
          { name: "0. FISH", note: "Folder specific for Fish LARVIVA",
            children: [
              { name: "¤ LARVIVA ORBIT", note: "Folder specific for LARVIVA ORBIT material" },
              { name: "Packaging Pictures", note: "Product packaging photos for LARVIVA Fish." },
              { name: "Adverts", note: "Advertisements for LARVIVA Fish." },
              { name: "Assets", note: "Artwork specific to LARVIVA fish" },
              { name: "Brochures", note: "Product brochures for LARVIVA Fish." },
              { name: "Datasheets", note: "Technical datasheets for LARVIVA Fish products." },
              { name: "ESB", note: "Email Signature Banners (ESB)" },
              { name: "Labels", note: "Product labels for LARVIVA Fish." },
              { name: "Merchandise", note: "Branded merchandise for LARVIVA Fish." },
              { name: "Overviews", note: "Product overview materials for LARVIVA Fish." },
              { name: "Presentations", note: "Presentation decks for LARVIVA Fish." }
            ]
          },
          { name: "0. SHRIMP", note: "Folder specific for Shrimp LARVIVA",
            children: [
              { name: "¤ Assets & Images", note: "Artwork specific to LARVIVA SHRIMP" },
              { name: "Adverts", note: "Advertisements for LARVIVA Shrimp." },
              { name: "Brochures", note: "Product brochures for LARVIVA Shrimp." },
              { name: "Datasheets", note: "Technical datasheets for LARVIVA Shrimp products." },
              { name: "ESB", note: "Email Signature Banners (ESB)" },
              { name: "Labels", note: "Product labels for LARVIVA Shrimp." },
              { name: "Merch", note: "Branded merchandise for LARVIVA Shrimp." },
              { name: "Packaging Pictures", note: "Product packaging photos for LARVIVA Shrimp." },
              { name: "PPT", note: "PowerPoint presentation decks for LARVIVA Shrimp." },
              { name: "Roll Ups", note: "Roll-up banner designs for LARVIVA Shrimp." },
              { name: "Videos", note: "Video assets for LARVIVA Shrimp." }
            ]
          }
        ]
      },
      { name: "3. ORBIT", note: "BioMar ORBIT shrimp-feed product line marketing and design assets.",
        children: [
          { name: "1. ORBIT Logo", note: "Product and sub-product logos. Print and digital logos." },
          { name: "Adverts", note: "General ORBIT Ads" },
          { name: "Brochures", note: "General ORBIT brochures" },
          { name: "Datasheets", note: "General ORBIT datasheets" },
          { name: "Merch", note: "General ORBIT merchandise" },
          { name: "Presentations", note: "General ORBIT presentations" },
          { name: "SoMe", note: "General ORBIT social media assets" },
          { name: "PPT", note: "General ORBIT PowerPoint templates" },
          { name: "Roll Ups", note: "General ORBIT roll-up banners" },
          { name: "Videos", note: "General ORBIT videos" }
        ]
      },
      { name: "4. EXIA", note: "Top-level folder for the EXIA feed product line and its sub-products and assets.",
        children: [
          { name: "□ Archive", note: "Archived or superseded files no longer in active use." },
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
              { name: "Adverts", note: "Print and digital adverts for the general EXIA range." },
              { name: "Brochures", note: "Brochures for the general EXIA range." },
              { name: "CN_Feed Bag", note: "Feed bag packaging designs (China) for the general EXIA range." },
              { name: "Datasheets", note: "Technical/product datasheets for the general EXIA range." },
              { name: "Feed samples", note: "Physical feed sample materials for the general EXIA range." },
              { name: "Merch", note: "Branded merchandise for the general EXIA range." },
              { name: "Poster", note: "Posters for the general EXIA range." },
              { name: "Roll up", note: "Roll-up banner designs for the general EXIA range." },
              { name: "SoMe", note: "Social media assets for the general EXIA range." }
            ]
          },
          { name: "VN_Celestial Harmony Line", note: "Customer-specific line in Vietnam",
            children: [
              { name: "ACTIVA COMET", note: "A specific variant/formulation of the EXIA ACTIVA product line." },
              { name: "PERFORM NOVA", note: "A specific variant/formulation of the EXIA PERFORM product line." },
              { name: "PRIME STAR", note: "A specific variant/formulation of the EXIA PRIME product line." }
            ]
          }
        ]
      },
      { name: "5. Blue Impact", note: "BioMar's sustainability-focused initiative and product line",
        children: [
          { name: "¤ Blue Impact Video", note: "Product Video" },
          { name: "¤ Campaigns", note: "Campaigns made by markets" },
          { name: "¤ Logo", note: "Blue Impact logo files" },
          { name: "Adverts", note: "Print and digital adverts" },
          { name: "Assets", note: "General design assets" },
          { name: "Billboards", note: "Billboard advert designs" },
          { name: "Brochures", note: "Brochures and printed materials" },
          { name: "Merchandise", note: "Branded merchandise designs" },
          { name: "PPTs", note: "PowerPoint presentation templates" }
        ]
      },
      { name: "6. INICIO and INTRO", note: "Top-level folder for the INICIO and INTRO product lines",
        children: [
          { name: "INICIO FISH", note: "INICIO product line materials for fish species",
            children: [
              { name: "□ Adverts", note: "General INICIO FISH Ads" },
              { name: "□ Assets", note: "General design assets for INICIO FISH" },
              { name: "□ Logos", note: "Product and sub-product logos for INICIO FISH" },
              { name: "□ Packaging Pictures", note: "Packaging photography for INICIO FISH" },
              { name: "Brochures", note: "Marketing brochures for INICIO FISH" },
              { name: "Documentation Material", note: "Technical and product documentation for INICIO FISH" },
              { name: "INICIO Akai", note: "Sub-product files" },
              { name: "INICIO Plus", note: "Sub-product files" },
              { name: "INICIO Plus M", note: "Sub-product files" },
              { name: "INICIO Plus S", note: "Sub-product files" },
              { name: "INICIO Quinnat", note: "Sub-product files" },
              { name: "INICIO Rainbow", note: "Sub-product files" }
            ]
          },
          { name: "INICIO Shrimp", note: "INICIO product line materials for shrimp",
            children: [
              { name: "□ INICIO Range", note: "General INICIO SHRIMP Material" },
              { name: "□ Logos", note: "Product and sub-product logos for INICIO Shrimp" },
              { name: "INICIO Focus", note: "Sub-product files" },
              { name: "INICIO Maxio", note: "Sub-product files" },
              { name: "INICIO Plus", note: "Sub-product files" },
              { name: "INICIO Prime", note: "Sub-product files" },
              { name: "INICIO Pro", note: "Sub-product files" },
              { name: "VN_Boxes_10kg", note: "General INICIO Box for Vietnam market" }
            ]
          },
          { name: "INTRO", note: "INTRO product line materials",
            children: [
              { name: "□ Logos", note: "Product and sub-product logos. Print and digital logos." },
              { name: "INTRO Plus MT", note: "Sub-product files" },
              { name: "INTRO Q", note: "Sub-product files" },
              { name: "INTRO Q+", note: "Sub-product files" },
              { name: "Presentations", note: "Sales and product presentations for INTRO" },
              { name: "Videos", note: "Video content for INTRO" }
            ]
          }
        ]
      },
      { name: "7. EFICO, MAXIO and POWER", note: "Feed product lines EFICO, MAXIO and POWER",
        children: [
          { name: "□ Brochures", note: "General Grower Brochures" },
          { name: "Assets", note: "Shared design assets for EFICO, MAXIO and POWER" },
          { name: "EFICO", note: "EFICO product line materials",
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
          { name: "MAXIO", note: "MAXIO product line materials",
            children: [
              { name: "□ Logos", note: "Product and sub-product logos. Print and digital logos." },
              { name: "□ MAXIO Range", note: "General MAXIO Material" },
              { name: "Maxio Barra", note: "Sub-product files" }
            ]
          },
          { name: "POWER", note: "POWER product line materials",
            children: [
              { name: "□ POWER Logos", note: "Product and sub-product logos. Print and digital logos." },
              { name: "□ POWER Range", note: "General MAXIO Material" },
              { name: "H2O", note: "Sub-product files" }
            ]
          }
        ]
      },
      { name: "8. BioFarm", note: "BioFarm brand assets, templates and marketing materials",
        children: [
          { name: "¤ BioFarm Logo", note: "All logo versions. Print and digital logos." },
          { name: "¤ BioFarm Manual", note: "Manuals adapted for different markets" },
          { name: "¤ Other BioFarm Logos", note: "Logos of BioFarm programmes, such as BioFarm Academy and BioFarm Online" },
          { name: "Document Templates", note: "Editable templates for BioFarm documents" },
          { name: "ESB", note: "ESB-related assets and materials for BioFarm" },
          { name: "Icons", note: "Icon graphics for BioFarm materials" },
          { name: "Merch", note: "Merchandise and promotional item designs" },
          { name: "Photos", note: "Photography assets for BioFarm" },
          { name: "PPT", note: "PowerPoint presentation templates and decks" },
          { name: "Videos", note: "Video content and assets for BioFarm" }
        ]
      },
      { name: "ASIA", note: "Asian market folders, covering China and Vietnam",
        children: [
          { name: "China", note: "China market design and marketing material",
            children: [
              { name: "□ Archive", note: "Archived material for the China market" },
              { name: "□ Billboards", note: "Billboard designs for China" },
              { name: "□ BioFarm pic", note: "Photos from BioFarm China" },
              { name: "□ Brochures", note: "Brochures for the China market" },
              { name: "□ Corporate", note: "Material for Corporate" },
              { name: "□ Factory_Office_Signage_Stationary", note: "Material for Factory" },
              { name: "□ Feed Bags", note: "Customized Product Bags" },
              { name: "□ Handouts", note: "Handout material for China" },
              { name: "□ Labels", note: "Product labels for China" },
              { name: "□ Logos", note: "JV logos" },
              { name: "□ Uniforms", note: "Uniform designs for China staff" },
              { name: "Icons", note: "Icon assets for China market material",
                children: [
                  { name: "Fish", note: "Fish icon assets" },
                  { name: "Gems", note: "Gem icon assets" }
                ]
              },
              { name: "Images", note: "Image assets for the China market" },
              { name: "Slides", note: "Presentation slides for China" },
              { name: "Storefronts", note: "Storefront designs for China" },
              { name: "Tech Centre Video-Subtitles", note: "Subtitled videos for the Tech Centre" }
            ]
          },
          { name: "Vietnam", note: "Vietnam market design and marketing material",
            children: [
              { name: "Archive", note: "Archived material for the Vietnam market" },
              { name: "Assets", note: "General design assets for Vietnam" },
              { name: "Business Cards", note: "Business card designs for Vietnam" },
              { name: "Conferences & Expos", note: "Material created for conferences and expos such as booths" },
              { name: "Corporate", note: "Material for Corporate" },
              { name: "Office", note: "Material for Office" },
              { name: "0. BioMar Viet Uc Guidelines", note: "Brand guidelines for BioMar Viet Uc" },
              { name: "1. BioMar Viet Uc Logo", note: "Logo files for BioMar Viet Uc" },
              { name: "2. Factory_Signage_Office", note: "Signage for factory and office in Vietnam" },
              { name: "ACTIVA", note: "Product exclusive for Vietnam market" },
              { name: "Leaflet", note: "Leaflets for the Vietnam market" },
              { name: "Merch", note: "Merchandise designs for Vietnam" },
              { name: "Photo", note: "Photos for the Vietnam market" },
              { name: "Signboards", note: "Signboard designs for Vietnam" },
              { name: "SoMe", note: "Social media material for Vietnam" },
              { name: "Visitor card", note: "Visitor card designs for Vietnam" }
            ]
          }
        ]
      },
      { name: "CORPORATE", note: "Corporate-level materials not tied to a specific product",
        children: [
          { name: "Archive", note: "Archived corporate files" },
          { name: "Business Cards", note: "Business Cards for BioMar Group" },
          { name: "Global Policies", note: "Company-wide policy documents" },
          { name: "Aarhus Office", note: "Aarhus office \"decor\"" },
          { name: "2025-10 Biomar corporate video", note: "BioMar corporate video, October 2025" },
          { name: "2025-01 BioMar Value Chain (unclear)", note: "BioMar value chain materials, January 2025" },
          { name: "Finance", note: "Finance department documents" },
          { name: "GDPR", note: "Data protection and privacy documents" },
          { name: "Health and Safety", note: "Workplace health and safety documents" },
          { name: "HR", note: "Human resources documents" },
          { name: "IT", note: "IT department documents" },
          { name: "Manufacturing", note: "Manufacturing documents" },
          { name: "Sourcing", note: "Sourcing and procurement documents" }
        ]
      },
      { name: "EMEA", note: "Shared drive materials for BioMar's EMEA markets",
        children: [
          { name: "¤ Archive", note: "Older or superseded EMEA materials kept for reference" },
          { name: "¤ Brochures", note: "Product and company brochures for EMEA markets" },
          { name: "¤ Business Cards", note: "Business Cards for EMEA Markets" },
          { name: "¤ Calendars", note: "Every year Wall Planners and Agendas for employees" },
          { name: "¤ Conferences & Expos", note: "Material created for conferences and expos such as booths" },
          { name: "¤ Datasheets", note: "Product Datasheets" },
          { name: "¤ Factory_Office_Signage", note: "Signage for factories and offices" },
          { name: "¤ Feed Catalogues", note: "Every year Feed Catalogues tailored per market" },
          { name: "¤ Feed Overviews", note: "Every year Feed overview tailored per specie and market" },
          { name: "¤ Handbooks", note: "Employee and product handbooks for EMEA" },
          { name: "¤ Lanyard ID Card", note: "Lanyard and ID card designs for staff" },
          { name: "¤ Posters", note: "Information Posters tailored in different languages" },
          { name: "¤ PPT_Presentations", note: "PowerPoint templates and presentations for EMEA" },
          { name: "¤ Videos", note: "Video content for EMEA markets" },
          { name: "5. DAN EX", note: "Product exclusive for EMEA Markets" },
          { name: "SoMe", note: "Social media assets for EMEA" },
          { name: "¤ BioMar Sagun", note: "Folder specific for the JV Company in Turkey",
            children: [
              { name: "¤ Archive", note: "Older or superseded BioMar Sagun materials kept for reference" },
              { name: "¤ Brochures", note: "Product and company brochures for BioMar Sagun" },
              { name: "¤ Calendars", note: "Every year Calendars for employees" },
              { name: "1. BioMar Sagun Logo", note: "All approved logos. Print and digital" },
              { name: "2. Business Cards", note: "Business cards for BioMar Sagun staff" },
              { name: "3. Feed Bag", note: "Feed bag packaging designs for BioMar Sagun" },
              { name: "4. Factory", note: "Factory-related materials for BioMar Sagun" },
              { name: "BioMar Sagun ESB", note: "Employer/staff branding materials for BioMar Sagun" },
              { name: "BioMar Sagun Lanyard", note: "Lanyard designs for BioMar Sagun staff" },
              { name: "BioMar Sagun Notebooks", note: "Notebook designs for BioMar Sagun" },
              { name: "BioMar Sagun Staff Photos", note: "Staff photos for BioMar Sagun" },
              { name: "SoMe", note: "Social media assets for BioMar Sagun" }
            ]
          }
        ]
      },
      { name: "GLOBAL", note: "Everything related to Global Marketing, meaning our team and things used globally",
        children: [
          { name: "□ Archive", note: "Older marketing files kept for reference",
            children: [
              { name: "□ BioRetain", note: "Materials related to the BioRetain product" },
              { name: "□ Brochures", note: "General BioMar Brochures" },
              { name: "□ Merch", note: "Branded merchandise materials" },
              { name: "3. Christmas", note: "Christmas-themed marketing materials" },
              { name: "4. Press Releases", note: "Archived company press releases" },
              { name: "BioMar Corporate Video", note: "BioMar's corporate video assets" },
              { name: "BioMar Tech Centre Video", note: "Video about the BioMar Tech Centre" },
              { name: "BioMar Technology Video", note: "Video about BioMar's technology" },
              { name: "Office Design Inspo", note: "Offices around the world images. Every now and then needs to be updated" },
              { name: "Screensaver & Desktop", note: "Screensaver and desktop wallpaper images" }
            ]
          },
          { name: "□ Design Hub", note: "Resources and materials for the Design Hub",
            children: [
              { name: "Design hub onboarding", note: "Onboarding materials for the Design Hub" },
              { name: "Design Hub Process", note: "Process to show new marketing managers or other collaborators" },
              { name: "Design Hub Task Report", note: "Report to do every end of the year on how many tasks we did" },
              { name: "Digital BCs project", note: "Digital business cards project materials" },
              { name: "Global policies platform", note: "Materials for the global policies platform" },
              { name: "The hub minute format", note: "Template for Design Hub meeting minutes" }
            ]
          },
          { name: "1. Campaigns", note: "Global marketing campaign assets",
            children: [
              { name: "□ Archived Campaigns", note: "Past campaigns kept for reference" },
              { name: "Better Feed. Better Fish. Better Food. Campaign (BFBF)", note: "A global marketing campaign" },
              { name: "Better Feed. Better Food. Campaign (BFBF)", note: "A global marketing campaign" },
              { name: "BioMar Farmers Campaign (BFC)", note: "A global marketing campaign" },
              { name: "Fish health videos 101", note: "Educational videos on fish health" },
              { name: "Grower Campaign (GC)", note: "A global marketing campaign" },
              { name: "Our Promise Campaign (OPC)", note: "A global marketing campaign" },
              { name: "Our Purpose Campaign (PRC)", note: "A global marketing campaign" },
              { name: "Sustainable Nutrition Campaign (SNC)", note: "A global marketing campaign" },
              { name: "The Swoosh", note: "Assets for the BioMar Swoosh brand element",
                children: [
                  { name: "We Are BioMar Campaign (WBC)", note: "A global marketing campaign" }
                ]
              }
            ]
          }
        ]
      },
      { name: "LATAM", note: "Design assets for BioMar's Latin America markets: Costa Rica and Ecuador.",
        children: [
          { name: "Costa Rica (CR)", note: "Design assets and templates for the Costa Rica market.",
            children: [
              { name: "¤ Business Cards", note: "Business card designs and templates for Costa Rica staff." },
              { name: "¤ Conferences & Expos", note: "Materials for Costa Rica trade shows, conferences and expos." },
              { name: "1. Corporate", note: "Corporate branding and identity assets for Costa Rica." },
              { name: "Adverts", note: "Advertisement designs for the Costa Rica market." },
              { name: "Agendas", note: "Event agenda templates and materials for Costa Rica." },
              { name: "Feed Bags", note: "Feed bag packaging designs for Costa Rica." },
              { name: "Invitations", note: "Invitation designs for Costa Rica events." },
              { name: "Merch", note: "Branded merchandise designs for Costa Rica." }
            ]
          },
          { name: "Ecuador (EC)", note: "Design assets and templates for the Ecuador market.",
            children: [
              { name: "1. Pictures", note: "Photo assets for the Ecuador market." },
              { name: "2. Videos", note: "Video assets for the Ecuador market." },
              { name: "Advertisements", note: "Advertisement designs for the Ecuador market." },
              { name: "Archive", note: "Older or retired design assets kept for reference, Ecuador." },
              { name: "Business Cards", note: "Business card designs and templates for Ecuador staff." },
              { name: "Calendars", note: "Calendar designs for the Ecuador market." },
              { name: "Conferences & Expos", note: "Materials for Ecuador trade shows, conferences and expos." },
              { name: "Feed Overviews", note: "Feed product overview materials for Ecuador." },
              { name: "Handouts", note: "Handout materials for Ecuador events and sales visits." },
              { name: "Invitations", note: "Invitation designs for Ecuador events." },
              { name: "Posters", note: "Poster designs for the Ecuador market." },
              { name: "Product Samples", note: "Product sample presentation materials for Ecuador." },
              { name: "Social Media", note: "Social media graphics for the Ecuador market." },
              { name: "Technical-Commercial Asset Guide", note: "Guide covering technical and commercial assets for Ecuador." }
            ]
          }
        ]
      },
      { name: "SALMON", note: "Salmon market region: Australia, Chile, Iceland, Norway, Scotland and shared salmon products",
        children: [
          { name: "Australia (AUS)", note: "Design assets for the Australia (AUS) salmon market",
            children: [
              { name: "Archive", note: "Archived design files for Australia" },
              { name: "Business Cards", note: "Business card designs for Australia" },
              { name: "ECOline", note: "...ol (unclear, cut off at image edge)" },
              { name: "Factory_Signage_Office", note: "Factory, signage and office designs for Australia" },
              { name: "Merch", note: "Merchandise designs for Australia" },
              { name: "SoMe", note: "Social media assets for Australia" }
            ]
          },
          { name: "Chile (CL)", note: "Design assets for the Chile (CL) salmon market",
            children: [
              { name: "Adverts", note: "Advertising designs for Chile" },
              { name: "Archive", note: "Archived design files for Chile" },
              { name: "Billboards", note: "Billboard designs for Chile" },
              { name: "Business Cards", note: "Business card designs for Chile" },
              { name: "Campaigns", note: "Marketing campaign assets for Chile" },
              { name: "Conferences & Expos", note: "Conference and expo materials for Chile" },
              { name: "Feed Bags", note: "Feed bag packaging designs for Chile" },
              { name: "Flags", note: "Flag designs for Chile" },
              { name: "Merch", note: "Merchandise designs for Chile" },
              { name: "Office", note: "Office design assets for Chile" },
              { name: "Posters", note: "Poster designs for Chile" },
              { name: "Photo Guidelines", note: "Photography guidelines for Chile" }
            ]
          },
          { name: "Iceland (IS)", note: "Design assets for the Iceland (IS) salmon market",
            children: [
              { name: "Conferences & Expos", note: "Conference and expo materials for Iceland" }
            ]
          },
          { name: "Norway (NO)", note: "Design assets for the Norway (NO) salmon market",
            children: [
              { name: "Archive", note: "Archived design files for Norway" },
              { name: "Big Bags", note: "Big bag packaging designs for Norway" },
              { name: "Business Cards", note: "Business card designs for Norway" },
              { name: "Conferences", note: "Conference materials for Norway" },
              { name: "Posters", note: "Poster designs for Norway" },
              { name: "Adverts", note: "Advertising designs for Norway" },
              { name: "Banners", note: "Banner designs for Norway" },
              { name: "Billboards", note: "Billboard designs for Norway" },
              { name: "FÖROPPLYSNINGEN", note: "Feed information/declaration materials for Norway" },
              { name: "Kvarøy Handout", note: "Handout materials for the Kvarøy site in Norway" },
              { name: "Merch", note: "Merchandise designs for Norway" },
              { name: "Myre Office", note: "Office design assets for the Myre site in Norway" },
              { name: "NO Portraits", note: "Portrait photography for Norway" },
              { name: "NO_Videos", note: "Video assets for Norway" },
              { name: "Roll-Up Banners", note: "Roll-up banner designs for Norway" },
              { name: "SoMe", note: "Social media assets for Norway" },
              { name: "SoMe_Winter Feed Strategy", note: "Social media assets for Norway's winter feed strategy" }
            ]
          },
          { name: "Scotland (UK)", note: "Design assets for the Scotland (UK) salmon market",
            children: [
              { name: "Archive", note: "Archived design files for Scotland" },
              { name: "Business Cards", note: "Business card designs for Scotland" },
              { name: "Conferences", note: "Conference materials for Scotland" },
              { name: "Adverts", note: "Advertising designs for Scotland" },
              { name: "Merch", note: "Merchandise designs for Scotland" },
              { name: "Office Design_Grangemouth", note: "Office design assets for the Grangemouth site in Scotland" },
              { name: "Truck", note: "Truck livery and vehicle designs for Scotland" }
            ]
          },
          { name: "SYMBIO", note: "Product exclusive for SALMON Markets" },
          { name: "¤ Tri X", note: "Product exclusive for SALMON Markets" }
        ]
      },
      { name: "RnD", note: "R&D (Research & Development) category folder — currently empty and not yet built out on the shared drive." },
      { name: "SALMON", note: "Salmon R&D and sustainability communications materials",
        children: [
          { name: "¤ Archive", note: "Older or superseded sustainability/R&D files kept for reference" },
          { name: "1. Sustainability Report", note: "Annual salmon sustainability report and related files" },
          { name: "2. BioSustain", note: "Materials for the BioSustain sustainability program" },
          { name: "3. BioSustain Masterclass", note: "Training/masterclass content for the BioSustain program" },
          { name: "4. White Papers", note: "Sustainability and R&D white papers" },
          { name: "Auchan Shrimp Video", note: "Promotional video made for Auchan shrimp partnership" },
          { name: "Discover Tool", note: "Interactive tool for exploring sustainability content" },
          { name: "EN_Our Ambition Videos", note: "English-language videos on sustainability ambitions" },
          { name: "PPTs", note: "Presentation decks for sustainability/R&D communications" }
        ]
      }
    ],
  },
];
