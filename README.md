# Dr. Jiang 'John' Li - Academic Website

A professional academic website built with Quarto showcasing Dr. Li's work as Program Chair for Analytics programs at Franklin University.

## 🚀 Quick Start

### Prerequisites
- [Quarto](https://quarto.org/docs/get-started/) installed
- R with required packages (lubridate)
- Git for version control

### Running the Website Locally

1. **Start the development server:**
   ```bash
   quarto preview --port 4200 --no-browser
   ```
   
2. **View the website:**
   Open your browser and navigate to `http://localhost:4200`

3. **Stop the server:**
   Press `Ctrl+C` in the terminal

### Building for Production

```bash
quarto render
```

This generates all HTML files in the project directory, ready for deployment.

## 📁 Project Structure

```
├── README.md                 # This file
├── _quarto.yml              # Main Quarto configuration
├── custom.scss              # Custom styling (Franklin University theme)
├── index.qmd                # Homepage
├── post.qmd                 # Posts/Blog listing page
├── program.qmd              # Analytics Programs page
├── course.qmd               # Courses page
├── teach.qmd                # Teaching Materials page
├── publication.qmd          # Publications page
├── img/                     # Images directory
│   └── jiang.jpg           # Profile photo
└── posts/                   # Blog posts and content
    ├── analytics_review/    # Analytics concept reviews
    │   └── flashcards.html # Interactive flip cards
    ├── job_application/     # Job application materials
    ├── job_listing/         # Job listing visualizations
    └── ...                  # Other posts
```

## 🎨 Customization

### Theme and Styling
- **Main theme**: Located in `custom.scss`
- **Franklin University colors**: Primary blue (#1f4e79)
- **Responsive design**: Mobile-first approach

### Key Style Classes
- `.btn-professional`: Blue buttons with white text
- `.btn-outline-professional`: Outline buttons
- `.hero-section`: Blue gradient header section
- `.achievement-card`: Content cards with hover effects

### Adding New Content

#### Adding a New Post
1. Create a new folder in `posts/` directory:
   ```bash
   mkdir posts/new-post-name
   ```

2. Add your content files (qmd, html, images, etc.)

3. Update `post.qmd` to include your new post in the listing

#### Updating Homepage
- Edit `index.qmd` for main content
- Profile photo: Replace `img/jiang.jpg`
- Contact information: Update email links and meeting scheduler

#### Adding New Pages
1. Create a new `.qmd` file in the root directory
2. Add navigation link in `_quarto.yml` under `navbar`

## 📝 Content Management

### LinkedIn Posts
Update the LinkedIn section in `post.qmd` with new posts:
- Add new entries in chronological order (newest first)
- Include date, title, and LinkedIn URL

### Publications
Update `publication.qmd` with new research papers and publications.

### Courses
Update `course.qmd` and `teach.qmd` with new course materials and teaching resources.

## 🔧 Maintenance Tasks

### Regular Updates
1. **Content refresh**: Update posts, courses, and achievements
2. **Dependencies**: Keep Quarto and R packages updated
3. **Images**: Optimize images for web performance
4. **Links**: Check and update external links

### Troubleshooting

#### Port Already in Use Error
```bash
# Kill process using port 4200
lsof -ti:4200 | xargs kill -9
# Or use a different port
quarto preview --port 4201 --no-browser
```

#### CSS Changes Not Showing
```bash
# Force rebuild
quarto render --clean
```

#### Missing Dependencies
```bash
# Install missing R packages
R -e "install.packages('lubridate')"
```

## 🚀 Deployment

### GitHub Pages (Recommended)
1. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "Update website content"
   git push origin main
   ```

2. **GitHub will automatically build and deploy** (if GitHub Actions is configured)

### Manual Deployment
1. **Build the site:**
   ```bash
   quarto render
   ```

2. **Upload files** to your web hosting service

## 📊 Features

### Interactive Elements
- **Analytics Flashcards**: 67 interactive concept review cards
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Professional Styling**: Franklin University branding
- **Contact Integration**: Direct email and meeting scheduler links

### SEO Optimized
- Semantic HTML structure
- Meta descriptions and titles
- Professional social media preview

## 🛠️ Development Notes

### Custom Components
- Hero section with two-column layout (photo + about)
- Achievement cards with hover effects
- Professional button styling
- Mobile-responsive navigation

### Performance
- Optimized images
- Minimal external dependencies
- Clean, semantic HTML output

## 📞 Support

For technical issues or questions about maintaining this website:
- Check Quarto documentation: https://quarto.org/docs/
- Review commit history for recent changes
- Contact: jiang.li2@franklin.edu

---

**Last Updated**: December 2024
**Quarto Version**: 1.x
**Theme**: Franklin University Professional 