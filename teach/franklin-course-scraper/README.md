# Franklin University Course Scraper

Automated web scraper for Franklin University course scheduling data, designed to extract real-time enrollment information for Analytics & Computer Science programs.

## 🎯 Overview

This project automates the collection of course section data from Franklin University's course search system, generating clean CSV output for analysis and reporting integration with Quarto websites.

## 📦 Features

- **Real-time data extraction** from Franklin University's course system
- **Headless browser automation** for efficient operation
- **Flexible course configuration** via markdown files
- **CSV output** ready for data analysis and reporting
- **First-term course tracking** for program planning
- **Robust error handling** and detailed logging
- **Automated report generation** with summary statistics and analytics
- **Beautiful Quarto-based scheduling interface** with enrollment insights

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)

### Installation
```bash
cd teach/franklin-course-scraper
pip install -r requirements.txt
```

### Usage

**Quick Update (Recommended):**
```bash
./update_schedule.sh
```

**Manual Steps:**
1. Configure courses in `course_request.md`
2. Run the scraper:
```bash
cd scripts
python scrape_franklin_courses.py
```
3. Regenerate report:
```bash
cd ../..
quarto render course-schedule.qmd
```
4. Check output in `data/franklin_courses.csv` and `_site/teach/course-schedule.html`

## ⚙️ Configuration

Edit `course_request.md` to specify:
- Target term (e.g., "Fall 2025")
- Course list with first-term indicators (*)

Example:
```markdown
Term: Fall 2025
*PF 521      # First-term course
DATA 610     # Regular course
*DATA 630    # First-term course
```

## 📊 Output Format

**CSV Data** (`data/franklin_courses.csv`):
- Course details (code, name, credits, term)
- Enrollment data (enrolled, available, total, waitlist)  
- Schedule information (weekdays, times, locations)
- Instructor and teaching mode
- Metadata (first-term status, scrape timestamp)

**HTML Report** (`../course-schedule.html`):
- Interactive course schedule table with filtering
- Summary statistics dashboard (enrollment, utilization)
- Program area analysis and insights
- First-term course recommendations
- Real-time availability status

## 🔧 Technical Details

- **Browser**: Headless Chrome with automation detection avoidance
- **Parsing**: BeautifulSoup for HTML processing
- **Performance**: Compiled regex patterns and optimized waits
- **Error handling**: Graceful fallbacks and detailed logging

## 📁 Project Structure

```
franklin-course-scraper/
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── course_request.md      # Course configuration
├── scripts/
│   └── scrape_franklin_courses.py
├── data/
│   └── franklin_courses.csv
├── output/                # Generated reports
└── config/                # Advanced configuration
```

## 🤝 Contributing

This is part of a larger academic automation project. For questions or improvements, please refer to the main project documentation.

## 📝 License

Part of Jiang Li's academic website automation suite. 