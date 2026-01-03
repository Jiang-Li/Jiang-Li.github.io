# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an academic website for Dr. Jiang 'John' Li, Program Chair for Analytics Programs at Franklin University. Built with Quarto, it features automated course data scraping from Franklin University's self-service portal with daily updates via GitHub Actions.

## Build and Development Commands

```bash
# Start development server
quarto preview --port 4200

# Build full website for production
quarto render

# Build single page (faster when working on specific content)
quarto render <file.qmd>

# Run the course scraper manually
cd teach/franklin-course-scraper
python scripts/scrape_franklin_courses.py
```

## Architecture

### Core Components

1. **Quarto Site** (`_quarto.yml`): Static site generator configuration with navbar, styling (cosmo theme + custom.scss), and page structure

2. **Course Scraper System** (`teach/franklin-course-scraper/`):
   - `scripts/scrape_franklin_courses.py`: Main scraper using Selenium + BeautifulSoup
   - `data/franklin_courses.csv`: Output file with scraped course data
   - `course_request.md`: Configuration file defining which courses to track and term

3. **Course Schedule Display** (`teach/course-schedule.qmd`): Quarto document that reads the CSV and generates an HTML table with frozen columns, first-term highlighting, and sticky headers

4. **GitHub Actions Workflow** (`.github/workflows/update-courses.yml`): Smart automation that:
   - Runs daily at 6 AM EST (11 AM UTC)
   - Only scrapes when course-related files change (detected via git diff)
   - Skips scraping dependencies for faster builds when only non-course files change
   - Deploys to GitHub Pages

### Course Scraper Details

The scraper (`scrape_franklin_courses.py`) extracts:
- Course sections (face-to-face only, filters out online/WW)
- Enrollment data (enrolled/total/waitlist format)
- Class times, weekdays, locations
- Instructor names
- Session codes
- Term information (filterable via `course_request.md`)

**Key parsing patterns**:
- Uses Franklin-specific weekday parsing (T=Tuesday, Th=Thursday, NOT R)
- Detects first-term courses via asterisk prefix in `course_request.md`
- Groups multiple sections of same course with semicolon separators
- Calculates enrolled seats = total - available
- Stores timestamps in EST timezone

**Data flow**: `course_request.md` → scraper → `franklin_courses.csv` → `course-schedule.qmd` → rendered HTML table

### Configuration Files

- `course_request.md`: Edit this to change:
  - Term (e.g., "Spring 2026")
  - Course list to track
  - First-term markers (prefix with `*`)
  - Format: `Term: Spring 2026` followed by course codes (one per line)

- `_quarto.yml`: Site structure, navbar, theme, and metadata

### Content Structure

- `index.qmd`: Homepage
- `teach.qmd`: Teaching hub with links to course schedule and materials
- `teach/course-schedule.qmd`: Live course schedule table
- `teach/analytics_review/flashcards.html`: Interactive learning materials
- `posts/`: Blog posts and interactive demos

### CSS and Styling

- `style.css`: Global styles
- `custom.scss`: Theme customization (extends cosmo)
- `teach/course-schedule.qmd` contains embedded styles for frozen columns, sticky headers, and first-term highlighting

### Python Dependencies

The scraper requires:
- selenium (headless Chrome automation)
- beautifulsoup4 (HTML parsing)
- webdriver-manager (automatic ChromeDriver management)
- pandas (data processing)

These are only installed by GitHub Actions when scraping is needed (smart triggering).

## Important Constraints

- The scraper only extracts FF (face-to-face) sections, filtering out online/WW sections
- Franklin University uses "Th" for Thursday, not "R"
- First-term course detection relies on asterisk prefix in `course_request.md`
- The workflow uses smart file-change detection to skip scraping when unnecessary
- All timestamps should be in EST timezone for consistency
- Course codes are formatted with asterisk (e.g., `DATA*610`) for the Franklin search URL
