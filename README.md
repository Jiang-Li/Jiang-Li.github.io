# Dr. Jiang 'John' Li - Academic Website

A professional academic website built with Quarto showcasing Dr. Li's work as Program Chair for Analytics programs at Franklin University.

## 🚀 Features

- **📊 Automated Course Scraping**: Daily updates of Franklin University course schedules with enrollment data, frozen columns, and first-term indicators
- **🎓 Interactive Learning**: 67+ analytics concept review flashcards with flip animations
- **📱 Responsive Design**: Franklin University branding, mobile-first approach  
- **🤖 GitHub Actions**: Automated daily course data updates at 6 AM EST with smart file-based triggering
- **🎯 Enhanced Display**: Sticky column headers, EST timezone display, and frozen first two columns for better navigation

## 🏃‍♂️ Quick Start

```bash
# Start development server
quarto preview --port 4200

# Build for production  
quarto render
```

## 📁 Key Structure

```
├── _quarto.yml              # Quarto configuration
├── index.qmd                # Homepage
├── teach.qmd                # Teaching materials & tools
├── teach/
│   ├── course-schedule.qmd  # Live course schedule with enhanced features
│   ├── analytics_review/    # Interactive learning materials
│   │   └── flashcards.html  # 67+ analytics concept flip cards
│   └── franklin-course-scraper/  # Course data automation
│       ├── scripts/scrape_franklin_courses.py
│       ├── data/franklin_courses.csv
│       └── course_request.md    # Courses to track
├── .github/workflows/       # Smart automated course updates
└── posts/                   # Blog posts and content
```

## 🤖 Course Scraper System

### Enhanced Features
- **Smart Scheduling**: Runs daily at 6 AM EST, only when course-related files change
- **14 Courses Tracked**: DATA, COMP, MATH, BUSA, ITEC programs  
- **Advanced Display**: Frozen columns, first-term highlighting, EST timezone
- **Real-time Enrollment**: Shows enrolled/capacity format with availability status
- **Improved Extraction**: Enhanced instructor detection logic with fallback patterns

### Course Schedule Display
- **Frozen Columns**: First two columns (Course, Section) stay visible during horizontal scrolling
- **First-term Indicators**: Blue badges and row highlighting for orientation courses
- **EST Timezone**: All timestamps displayed consistently in Eastern time
- **Smart Styling**: Hover effects, alternating row colors, and responsive design

### Manual Updates
```bash
cd teach/franklin-course-scraper
python scripts/scrape_franklin_courses.py
```

### Configuration
Edit `teach/franklin-course-scraper/course_request.md` to modify tracked courses:
```
Term: Fall 2025
*PF 521        # * marks first-term courses
DATA 610
*DATA 630
# ... more courses
```

## 🎨 Content Management

### Teaching Materials
- **Analytics Flip Cards**: Interactive 67+ concept review cards with progress tracking
- **Course Schedule**: Live enrollment data with enhanced navigation features
- **Analytics Teaching Hub**: Instructor resources (Franklin account required)

### Adding Posts
1. Create folder in `posts/new-post-name/`
2. Add content files (qmd, html, images)
3. Update `post.qmd` listing

### Updating Courses
- **Automatic**: GitHub Actions with smart triggering on file changes
- **Manual**: Run scraper script and commit changes
- **Configuration**: Edit course request file for new terms

## 🚀 Deployment

**Automatic**: GitHub Actions builds and deploys on push to main branch with optimized workflow

**Manual**:
```bash
git add . && git commit -m "Update content" && git push
```

## 🛠️ Tech Stack

- **Frontend**: Quarto, HTML/CSS/JS with enhanced styling
- **Automation**: Python, Selenium, BeautifulSoup with improved extraction logic
- **CI/CD**: GitHub Actions with smart file-based triggering
- **Deployment**: GitHub Pages
- **Data**: CSV, Pandas with EST timezone handling

## 📞 Contact

- **Email**: jiang.li2@franklin.edu
- **Website**: [https://jiang-li.github.io](https://jiang-li.github.io)
- **Documentation**: [Quarto Docs](https://quarto.org/docs/)

---

**Enhanced course display** • **Interactive learning tools** • **Smart automation** • **Built with Quarto** 