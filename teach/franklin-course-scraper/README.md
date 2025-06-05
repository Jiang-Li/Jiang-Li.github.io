# Franklin University Course Scraper

Automated web scraper for Franklin University course scheduling data with enhanced display features, smart scheduling, and improved data extraction for Analytics & Computer Science programs.

## 🎯 Overview

This project automates the collection of course section data from Franklin University's course search system, generating clean CSV output with advanced display features for Quarto-based course schedule integration.

## 📦 Features

- **Real-time data extraction** from Franklin University's course system
- **Enhanced display features** with frozen columns, first-term indicators, and EST timezone
- **Smart instructor detection** with improved extraction logic and fallback patterns
- **Headless browser automation** for efficient operation
- **Flexible course configuration** via markdown files
- **CSV output** optimized for enhanced table display
- **First-term course tracking** with visual indicators
- **Robust error handling** and detailed logging
- **EST timezone consistency** for all timestamps
- **Advanced table features** including sticky headers and frozen columns

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

**Manual Run:**
```bash
python scripts/scrape_franklin_courses.py
```

**Check Output:**
- **CSV Data**: `data/franklin_courses.csv`
- **Quarto Display**: Navigate to parent directory and run `quarto preview course-schedule.qmd`

## ⚙️ Configuration

Edit `course_request.md` to specify:
- Target term (e.g., "Fall 2025")
- Course list with first-term indicators (*)

Example:
```markdown
Term: Fall 2025
*PF 521      # First-term course (gets blue badge)
DATA 610     # Regular course
*DATA 630    # First-term course
```

## 📊 Enhanced Output Features

**CSV Data Structure** (`data/franklin_courses.csv`):
- Course details (code, name, credits, term)
- Enrollment data (enrolled, total, waitlist) - removed Available_Seats column
- Schedule information (weekdays, times, locations)
- Instructor information with improved extraction logic
- Teaching mode and date ranges
- First-term status and EST timestamps

**Advanced Display Features**:
- **Frozen Columns**: First two columns (Course, Section) remain visible during scrolling
- **First-term Indicators**: Blue badges and row highlighting for orientation courses
- **EST Timezone**: Consistent timezone display for all timestamps
- **Enhanced Styling**: Hover effects, alternating row colors, responsive design
- **Smart Enrollment Display**: Shows enrolled/capacity format instead of separate columns

## 🔧 Technical Enhancements

### Instructor Extraction
- **Primary Method**: Searches for specific `search-sectioninstructormethods` cells
- **Enhanced Patterns**: Looks for spans with Faculty Office Hours aria-labels
- **Fallback Logic**: General text pattern matching with improved filtering
- **Smart Filtering**: Excludes keywords like "seats", "room", "time", course codes
- **Name Recognition**: Detects proper name patterns (First Last, Last, First)

### Timezone Handling
- **EST Consistency**: All scraped timestamps saved in Eastern Standard Time
- **ISO Format**: Uses ISO format with timezone indicators (-05:00)
- **Display Optimization**: Simplified parsing for consistent EST display

### Data Optimization
- **Removed Available_Seats**: Streamlined display showing only enrolled/capacity
- **Enhanced Course Codes**: Proper asterisk and section code extraction
- **Improved Error Handling**: Graceful fallbacks for missing data

## 📁 Project Structure

```
franklin-course-scraper/
├── README.md              # This file  
├── course_request.md      # Course configuration
├── scripts/
│   ├── scrape_franklin_courses.py  # Main scraper with enhancements
│   └── franklin_scraper_ref.py     # Reference implementation
├── data/
│   └── franklin_courses.csv        # Enhanced output format
└── requirements.txt       # Python dependencies
```

## 🎯 Integration Features

**Quarto Course Schedule Integration**:
- **Frozen Column CSS**: Sticky positioning for first two columns with proper z-index
- **First-term Styling**: Blue badges and row highlighting
- **Responsive Design**: Mobile-friendly table with horizontal scrolling
- **Progress Tracking**: Shows enrollment status with color coding
- **Real-time Updates**: Data refreshed via GitHub Actions on file changes

**GitHub Actions Optimization**:
- **Smart Triggering**: Only runs when course-related files change
- **Workflow Efficiency**: Removed redundant steps, saved 37 lines
- **Conditional Dependencies**: Python packages installed only when needed
- **EST Scheduling**: Runs at 6 AM EST instead of UTC

## 🤝 Integration

This scraper integrates with:
- **Parent Quarto Site**: `../course-schedule.qmd` for enhanced display
- **GitHub Actions**: `.github/workflows/update-courses.yml` for automation
- **Teaching Materials**: Part of broader academic tools ecosystem

## 📝 Recent Improvements

- **Enhanced Instructor Logic**: Better detection patterns with multiple fallback methods
- **Frozen Columns**: CSS implementation for improved table navigation  
- **EST Timezone**: Consistent timestamp handling and display
- **Smart Workflow**: File-based triggering reduces unnecessary runs
- **Display Optimization**: Removed redundant columns, improved styling
- **Error Handling**: More robust parsing with graceful degradation

## 📞 Support

Part of Dr. Jiang Li's academic website automation suite. For technical details, see the main project documentation. 