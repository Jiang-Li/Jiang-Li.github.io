#!/bin/bash

# Franklin Course Schedule Update Script
# This script updates the course data and regenerates the schedule report

echo "🎯 Franklin Course Schedule Update"
echo "=================================="

# Navigate to scraper directory
cd "$(dirname "$0")/scripts"

echo "📊 Step 1: Running course scraper..."
python scrape_franklin_courses.py

if [ $? -eq 0 ]; then
    echo "✅ Scraper completed successfully"
    
    # Navigate back to teach directory
    cd ../../
    
    echo "📝 Step 2: Regenerating course schedule report..."
    quarto render course-schedule.qmd
    
    if [ $? -eq 0 ]; then
        echo "✅ Course schedule updated successfully!"
        echo "📍 View at: _site/teach/course-schedule.html"
    else
        echo "❌ Failed to regenerate report"
        exit 1
    fi
else
    echo "❌ Scraper failed"
    exit 1
fi

echo ""
echo "🎉 Update complete! Your course schedule is now current." 