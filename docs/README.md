# Ted Huang Project Hub Documentation

This document explains the data models, categorization schemes, and deployment processes for this site.

## Site Article Metadata Schema

Both the central hub (`hub.json`) and individual project repositories (`site/page.json`) rely on structured JSON metadata. These objects populate the HTML tags and structured data for the site.

### `page.json` (Project Repositories)

Each project repository defines a `page.json` file inside its `site/` folder. This file describes the project and handles bilingual fields (`"en"` and `"zh"`).

**Required Fields:**
- `repo`: The repository owner and name (e.g., `owner/repo-name`).
- `slug`: The exact repository name, used in URLs.
- `name`: The project's title/name.
- `mark`: A 1-to-3 character abbreviation for the project tile.
- `title`, `description`, `hero`, `capabilities`, `status`, `facts`: Objects representing sections of the project page.

**Optional Fields:**
- `palette`: A theming color selection (`lime`, `violet`, etc.).
- `stats`, `flow`, `showcase`, `architecture`, `decisions`, `quickstart`, `links`.

### `hub.json` (Project Objects)

The hub repository's `hub.json` maintains the list of projects in a flat structure, adding grouping context.

**Fields include:**
- All common fields mentioned above.
- `group`: An identifier linking the project to a section on the hub (e.g., `ai-tools`).
- `page`: Explicit links for custom language routes (for projects with external websites).

## Tag Taxonomy

The hub utilizes tags to visually communicate characteristics of a project and grouping logic to organize the project list.

### Groups (in `hub.json`)

Projects are organized into four main groups.
- **`ai-tools`**: AI tools and utilities.
- **`agents`**: Agent-based tools and operations.
- **`security`**: Security and IT operations.
- **`small`**: Smaller projects, toys, and notes.

### Capability Tags (in project pages)

Individual capabilities defined in a project's `page.json` (`capabilities` array) often contain a `tag` field. This string tag renders as a visual badge on the corresponding capability card, conveying additional technical details or characteristics of that specific feature.

## Static Build Deployment Workflow

This project is a static site generated via Python standard library tools. There is no runtime or client-side build process required.

1. **Content Modification:** Edit `hub.json` or a project's `site/page.json`.
2. **Build Process:**
    - To generate the main hub directory, run: `python3 kit/render_hub.py .`
    - To build an individual project page locally, run: `python3 kit/render.py path/to/repo`
3. **Validation (Optional):** Run Python/Node tests using `node --test kit/flow.test.js` and `python3 -m unittest discover kit`.
4. **Commit:** Ensure `site/` output directories are committed alongside the JSON changes.
5. **Deployment:** The GitHub Actions workflow located in `.github/workflows/pages.yml` automatically triggers on push to the `main` branch. It serves the contents of the `site/` directory using GitHub Pages.

No extra tooling (like Webpack or npm) is used for rendering. All static files (CSS/JS) reside in the `kit/` directory and are copied directly when applicable.