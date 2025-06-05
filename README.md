# Dr. Jiang 'John' Li - Academic Website

A professional academic website built with Quarto showcasing Dr. Li's work as Program Chair for Analytics programs at Franklin University.

## 🚀 Features

- **📊 Automated Course Scraping**: Daily updates of Franklin University course schedules with enrollment data
- **🎓 Interactive Learning**: 67+ analytics concept review flashcards
- **📱 Responsive Design**: Franklin University branding, mobile-first approach
- **🤖 GitHub Actions**: Automated daily course data updates at 6 AM

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
├── teach.qmd                # Teaching materials
├── teach/course-schedule.qmd # Live course schedule
├── teach/franklin-course-scraper/  # Course data automation
│   ├── scripts/scrape_franklin_courses.py
│   ├── data/franklin_courses.csv
│   └── course_request.md    # Courses to track
├── .github/workflows/       # Automated course updates
└── posts/                   # Blog posts and content
```

## 🤖 Course Scraper System

### Automated Features
- **Daily Scraping**: Runs every day at 6 AM UTC via GitHub Actions
- **14 Courses Tracked**: DATA, COMP, MATH, BUSA, ITEC programs
- **Real-time Enrollment**: Shows enrolled/total/available seats
- **First-term Highlighting**: Special marking for orientation courses

### Manual Updates
```bash
cd teach/franklin-course-scraper/scripts
python scrape_franklin_courses.py
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

### Adding Posts
1. Create folder in `posts/new-post-name/`
2. Add content files (qmd, html, images)
3. Update `post.qmd` listing

### Updating Courses
- **Automatic**: GitHub Actions updates daily
- **Manual**: Run scraper script and commit changes
- **Configuration**: Edit course request file

## 🚀 Deployment

**Automatic**: GitHub Actions builds and deploys on push to main branch

**Manual**:
```bash
git add . && git commit -m "Update content" && git push
```

## 🛠️ Tech Stack

- **Frontend**: Quarto, HTML/CSS/JS
- **Automation**: Python, Selenium, BeautifulSoup
- **CI/CD**: GitHub Actions
- **Deployment**: GitHub Pages
- **Data**: CSV, Pandas

## 📞 Contact

- **Email**: jiang.li2@franklin.edu
- **Documentation**: [Quarto Docs](https://quarto.org/docs/)

---

**Auto-updated course data** • **Built with Quarto** • **Franklin University branding** 