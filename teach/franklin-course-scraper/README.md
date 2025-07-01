# Franklin University Course Scraper

Automated web scraper for Franklin University course scheduling data with enhanced display features, smart scheduling, and advanced weekday pattern recognition for Analytics & Computer Science programs.

## 🎯 Overview

This project automates the collection of course section data from Franklin University's course search system, generating clean CSV output with advanced display features for Quarto-based course schedule integration. Features intelligent parsing of complex schedule patterns including T/Th, M/W/F, and other multi-day formats.

## 📦 Features

- **Real-time data extraction** from Franklin University's course system
- **Enhanced weekday parsing** with T/Th pattern recognition and chronological ordering
- **Advanced display features** with dynamic column sizing and frozen columns
- **Smart instructor detection** with improved extraction logic and fallback patterns
- **Intelligent time formatting** with proper weekday-time pairing and semicolon separation
- **Headless browser automation** for efficient operation
- **Flexible course configuration** via markdown files
- **CSV output** optimized for enhanced table display
- **First-term course tracking** with visual indicators
- **Robust error handling** and detailed logging
- **EST timezone consistency** for all timestamps
- **Dynamic column widths** that adjust to content length automatically

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
- Enrollment data (enrolled, total, waitlist)
- **Enhanced schedule information** with proper weekday parsing and chronological ordering
- Instructor information with improved extraction logic
- Teaching mode and date ranges
- First-term status and EST timestamps

**Advanced Display Features**:
- **Dynamic Column Sizing**: Columns automatically adjust to content length for optimal display
- **Enhanced Weekday Parsing**: Recognizes T/Th, M/W/F, and complex schedule patterns
- **Chronological Ordering**: Weekdays displayed in proper order (Mon, Tue, Wed, Thu, Fri)
- **Frozen Columns**: First two columns (Course, Section) remain visible during scrolling
- **First-term Indicators**: Blue badges and row highlighting for orientation courses
- **EST Timezone**: Consistent timezone display for all timestamps
- **Smart Time Formatting**: Proper weekday-time pairing with semicolon separation
- **Enhanced Styling**: Hover effects, alternating row colors, responsive design

## 🔧 Technical Enhancements

### Advanced Weekday Pattern Recognition
- **T/Th Pattern Support**: Specific regex patterns for Tuesday/Thursday combinations
- **Slash-separated Formats**: Handles T/Th, M/W, M/W/F, and other variations
- **Multiple Time Handling**: Courses with different times on different days
- **Chronological Sorting**: Weekdays automatically ordered Monday through Sunday
- **Enhanced Parsing Logic**: Improved `parse_weekdays()` function with comprehensive mapping

### Enhanced Schedule Display
- **Multiple Weekday Support**: Handles courses meeting multiple days with same/different times
- **Smart Time Combination**: Automatically pairs weekdays with corresponding times
- **Semicolon Separation**: Clean display of multiple meeting times (e.g., "Tue 10:00 AM - 12:00 PM; Thu 10:00 AM - 12:00 PM")
- **Dynamic Formatting**: Adapts display based on single vs. multiple meeting patterns

### Automatic Column Sizing
- **Content-Driven Widths**: JavaScript automatically measures and adjusts column widths
- **Responsive Positioning**: Second column position updates based on first column width
- **Mobile Optimization**: Maintains functionality across different screen sizes
- **Performance Optimized**: Calculations run on page load and window resize

### Instructor Extraction
- **Primary Method**: Searches for specific `search-sectioninstructormethods` cells
- **Enhanced Patterns**: Looks for spans with Faculty Office Hours aria-labels
- **Fallback Logic**: General text pattern matching with improved filtering
- **Smart Filtering**: Excludes keywords like "seats", "room", "time", course codes
- **Name Recognition**: Detects proper name patterns (First Last, Last, First)

### Location and Time Processing
- **Enhanced Location Extraction**: Better detection of building names and room numbers
- **Downtown Filtering**: Automatic removal of redundant "Downtown" prefix
- **Building Pattern Recognition**: Specific patterns for "Frasch Hall 422" and similar formats
- **Time Format Standardization**: Consistent spacing and formatting for all time ranges

### Timezone Handling
- **EST Consistency**: All scraped timestamps saved in Eastern Standard Time
- **ISO Format**: Uses ISO format with timezone indicators (-05:00)
- **Display Optimization**: Simplified parsing for consistent EST display

### Data Optimization
- **Enhanced Course Codes**: Proper asterisk and section code extraction
- **Improved Error Handling**: Graceful fallbacks for missing data
- **Robust Pattern Matching**: Multiple regex patterns for complex schedule formats

## 📁 Project Structure

```
franklin-course-scraper/
├── README.md              # This file  
├── course_request.md      # Course configuration
├── scripts/
│   ├── scrape_franklin_courses.py  # Main scraper with T/Th recognition
│   └── franklin_scraper_ref.py     # Reference implementation
├── data/
│   └── franklin_courses.csv        # Enhanced output format
└── requirements.txt       # Python dependencies
```

## 🎯 Integration Features

**Quarto Course Schedule Integration**:
- **Dynamic Column CSS**: Automatic width calculation with sticky positioning
- **Advanced Time Display**: Proper weekday ordering and time formatting
- **First-term Styling**: Blue badges and row highlighting
- **Enhanced Mobile Support**: Responsive design with dynamic column sizing
- **Progress Tracking**: Shows enrollment status with color coding
- **Real-time Updates**: Data refreshed via GitHub Actions on file changes

**GitHub Actions Optimization**:
- **Smart Triggering**: Only runs when course-related files change
- **Workflow Efficiency**: Streamlined process with conditional dependencies
- **EST Scheduling**: Runs at 6 AM EST for optimal data freshness

## 🤝 Integration

This scraper integrates with:
- **Parent Quarto Site**: `../course-schedule.qmd` for enhanced display
- **GitHub Actions**: `.github/workflows/update-courses.yml` for automation
- **Teaching Materials**: Part of broader academic tools ecosystem

## 📝 Recent Improvements

### Version 2.0 - Advanced Pattern Recognition (June 2025)
- **T/Th Pattern Recognition**: Specific regex patterns for complex weekday combinations
- **Enhanced Weekday Parsing**: Comprehensive mapping including "Th" → "Thursday"
- **Chronological Ordering**: Automatic weekday sorting (Monday, Tuesday, Wednesday, etc.)
- **Dynamic Column Sizing**: Content-driven width calculation for optimal display
- **Multiple Time Support**: Handles courses with different times on different days
- **Improved Location Extraction**: Better building/room detection and cleaning

### Previous Improvements
- **Enhanced Instructor Logic**: Better detection patterns with multiple fallback methods
- **Frozen Columns**: CSS implementation for improved table navigation  
- **EST Timezone**: Consistent timestamp handling and display
- **Smart Workflow**: File-based triggering reduces unnecessary runs
- **Display Optimization**: Improved styling and user experience
- **Error Handling**: More robust parsing with graceful degradation

## 🔍 Pattern Recognition Examples

The scraper now handles complex schedule patterns:

- **T/Th** → "Tue 10:00 AM - 12:00 PM; Thu 10:00 AM - 12:00 PM"
- **M/W/F** → "Mon 9:00 AM - 10:00 AM; Wed 9:00 AM - 10:00 AM; Fri 9:00 AM - 10:00 AM"
- **Single Days** → "Thu 6:00 PM - 9:40 PM"
- **Mixed Times** → "Mon 1:00 PM - 3:00 PM; Wed 10:00 AM - 12:00 PM"

## 📞 Support

Part of Dr. Jiang Li's academic website automation suite. For technical details, see the main project documentation. 