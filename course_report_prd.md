# Franklin University Course Analytics System - PRD v2.0

## 📋 **Project Overview**

**Objective:** Automate daily collection of Franklin University course information using Python/Selenium, generate professional analytics reports, and publish them as a dedicated page accessible from the Teaching section of your academic website.

**Key Benefits:**
- 🤖 **Fully Automated** - GitHub Actions runs daily without manual intervention
- 📊 **Professional Analytics** - Course enrollment trends, capacity analysis, program insights
- 🌐 **Dedicated Report Page** - Professional standalone report with link from Teaching page
- 💼 **Portfolio Enhancement** - Demonstrates automation, data analysis, and web development skills
- 🎯 **Program Support** - Real insights for curriculum planning and enrollment management

---

## 🏗️ **Technical Architecture**

### **High-Level Workflow**
```
Daily 6 AM EST → GitHub Actions → Scraper (Data Collection) → 
Report Generator (Analysis) → Quarto Render → Deploy → Live Report Page
```

### **Two-Script Architecture**
1. **`scrape_franklin_courses.py`** - Pure data collection
   - Reads `course_request.md` configuration
   - Scrapes Franklin University course catalog
   - Outputs clean CSV data to `data/` directory
   - No analysis or reporting logic

2. **`generate_course_report.py`** - Pure report generation
   - Reads CSV data from `data/` directory
   - Generates beautiful Quarto report
   - Creates interactive visualizations
   - Updates Teaching page with report link

### **Components:**
1. **Scheduler:** GitHub Actions cron job (daily 6 AM EST)
2. **Data Collection:** Python + Selenium + Chrome headless
3. **Data Storage:** CSV files in `data/` directory
4. **Report Generation:** Python + Pandas + Plotly + Quarto
5. **Web Integration:** Link from Teaching page to dedicated report page
6. **Deployment:** GitHub Pages automatic deployment

---

## 📁 **File Structure**

```
├── .github/workflows/
│   └── daily-course-report.yml          # GitHub Actions automation
├── scripts/
│   ├── scrape_franklin_courses.py       # Data collection script
│   ├── generate_course_report.py        # Report generation script
│   └── requirements.txt                 # Python dependencies
├── data/
│   ├── franklin_courses.csv             # Raw course data (updated daily)
│   └── course_analytics.json            # Processed analytics data
├── teach/
│   └── course-analytics.qmd             # Dedicated report page
├── course_request.md                     # Course configuration file
├── teach.qmd                            # Teaching page (contains link to report)
└── course_report_prd.md                 # This PRD document
```

---

## 🎯 **User Experience**

### **Teaching Page Integration**
- Teaching page (`teach.qmd`) contains a **Course Analytics Dashboard** section
- Professional callout box with description and features
- **Prominent link** to the dedicated report page: `teach/course-analytics.html`
- Brief overview of automation and data collection

### **Dedicated Report Page**
- Standalone professional report at `/teach/course-analytics.html`
- Beautiful visualizations and tables
- Real-time enrollment data and trends
- Downloadable CSV data link
- Professional branding consistent with site theme

---

## 🛠️ **Implementation Plan**

### **Phase 1: File Organization**
```bash
# Create proper directory structure
mkdir -p .github/workflows scripts data teach
```

### **Phase 2: Data Collection Script**
**File:** `scripts/scrape_franklin_courses.py`
- Port existing scraper logic
- Read configuration from `course_request.md`
- Output to `data/franklin_courses.csv`
- Include comprehensive error handling
- Performance optimizations for GitHub Actions

### **Phase 3: Report Generation Script**
**File:** `scripts/generate_course_report.py`
- Read CSV data from `data/` directory
- Generate `teach/course-analytics.qmd`
- Create interactive visualizations
- Calculate enrollment statistics
- Export processed data to JSON

### **Phase 4: GitHub Actions Workflow**
**File:** `.github/workflows/daily-course-report.yml`
- Daily schedule (6 AM EST)
- Install dependencies and Chrome
- Run data collection script
- Run report generation script
- Render Quarto site
- Deploy to GitHub Pages

### **Phase 5: Teaching Page Integration**
- Update `teach.qmd` with Course Analytics Dashboard section
- Add professional description and link
- Ensure consistent styling and branding

---

## 📊 **Data Flow**

### **Input:** `course_request.md`
```
Term: Fall 2025
*PF 521        # First-term course
DATA 610       # Regular course
*DATA 630      # First-term course
...
```

### **Step 1:** Data Collection → `data/franklin_courses.csv`
```csv
Course_Code,Session_Code,Course_Name,Credits,Term,Enrolled_Seats,Available_Seats,Total_Seats,Waitlist,Weekdays,Class_Times,Locations,Instructors,Teaching_Mode,Start_Date,End_Date,First_Term,Scraped_DateTime
```

### **Step 2:** Report Generation → `teach/course-analytics.qmd`
- Professional Quarto document
- Interactive charts and tables
- Summary statistics
- Trend analysis

### **Output:** Live report page at `/teach/course-analytics.html`

---

## 🔧 **Technical Requirements**

### **Python Dependencies** (`scripts/requirements.txt`)
```txt
selenium==4.15.2
beautifulsoup4==4.12.2
pandas==2.1.3
plotly==5.17.0
quarto==1.4.0
requests==2.31.0
lxml==4.9.3
```

### **GitHub Actions Environment**
- Ubuntu latest
- Python 3.11
- Chrome + ChromeDriver
- Quarto CLI
- GitHub Pages deployment permissions

---

## 🧪 **Testing Strategy**

### **Local Testing**
1. **Test Data Collection:**
   ```bash
   cd scripts
   python scrape_franklin_courses.py
   # Verify data/franklin_courses.csv is created
   ```

2. **Test Report Generation:**
   ```bash
   python generate_course_report.py
   # Verify teach/course-analytics.qmd is created
   ```

3. **Test Quarto Rendering:**
   ```bash
   quarto render
   quarto preview
   # Verify report page works at localhost:4200/teach/course-analytics.html
   ```

### **GitHub Actions Testing**
1. Manual workflow trigger
2. Monitor logs for each step
3. Verify automated deployment
4. Validate report page accessibility

---

## 📈 **Success Metrics**

### **Technical Success**
- ✅ Daily automated data collection (>95% success rate)
- ✅ Clean CSV data with all required fields
- ✅ Professional report page renders correctly
- ✅ Zero manual intervention required

### **Business Value**
- 📊 Real-time insights into course enrollment
- 🎯 Support for curriculum planning decisions
- 💼 Portfolio demonstration of automation skills
- 🌐 Professional web presence enhancement

---

## 🚀 **Future Enhancements**

### **Phase 2 Features**
- Historical trend analysis
- Enrollment prediction models
- Email alerts for capacity changes
- Mobile-responsive design improvements

### **Phase 3 Features**
- Multi-semester comparison
- Competitor analysis
- Student success correlation
- API endpoints for data access

---

*Document Version: 2.0 | Updated: January 2025 | Status: Ready for Implementation*
