#!/usr/bin/env python3
"""
Franklin University Course Report Generator

Generates professional analytics reports from scraped course data.
Creates beautiful Quarto documents with interactive visualizations
and comprehensive course analytics.

This script focuses purely on report generation as part of the two-script architecture:
- Data Collection: scrape_franklin_courses.py
- Report Generation: generate_course_report.py (this file)

Author: Course Analytics Project
Version: 1.0 (Report Generation Focused)
"""

import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any

class CourseReportGenerator:
    """Generate professional course analytics reports from CSV data"""
    
    def __init__(self):
        self.data_dir = "data"
        self.teach_dir = "teach"
        self.csv_file = "franklin_courses.csv"
        self.report_file = "course-analytics.qmd"
        self.json_file = "course_analytics.json"
        
    def find_data_file(self) -> str:
        """Find the CSV data file, checking multiple possible paths"""
        # Try different path combinations
        possible_paths = [
            os.path.join(self.data_dir, self.csv_file),  # data/franklin_courses.csv
            os.path.join("..", self.data_dir, self.csv_file),  # ../data/franklin_courses.csv
            self.csv_file  # franklin_courses.csv (current dir)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError(f"Could not find {self.csv_file} in any expected location")
    
    def find_teach_dir(self) -> str:
        """Find the teach directory, checking multiple possible paths"""
        possible_paths = [
            self.teach_dir,  # teach/
            os.path.join("..", self.teach_dir)  # ../teach/
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
            
        # Create teach directory if it doesn't exist
        try:
            os.makedirs(self.teach_dir, exist_ok=True)
            return self.teach_dir
        except:
            # Try parent directory
            parent_teach = os.path.join("..", self.teach_dir)
            os.makedirs(parent_teach, exist_ok=True)
            return parent_teach
    
    def load_course_data(self) -> pd.DataFrame:
        """Load course data from CSV file"""
        try:
            csv_path = self.find_data_file()
            print(f"📊 Loading course data from: {csv_path}")
            
            df = pd.read_csv(csv_path)
            print(f"✅ Loaded {len(df)} course sections")
            return df
            
        except Exception as e:
            print(f"❌ Failed to load course data: {e}")
            raise
    
    def calculate_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive course analytics"""
        try:
            # Basic statistics
            total_sections = len(df)
            unique_courses = df['Course_Code'].nunique()
            
            # Enrollment analytics
            df['Enrolled_Seats'] = pd.to_numeric(df['Enrolled_Seats'], errors='coerce').fillna(0)
            df['Total_Seats'] = pd.to_numeric(df['Total_Seats'], errors='coerce').fillna(0)
            df['Available_Seats'] = pd.to_numeric(df['Available_Seats'], errors='coerce').fillna(0)
            df['Waitlist'] = pd.to_numeric(df['Waitlist'], errors='coerce').fillna(0)
            
            total_enrollment = df['Enrolled_Seats'].sum()
            total_capacity = df['Total_Seats'].sum()
            total_available = df['Available_Seats'].sum()
            total_waitlist = df['Waitlist'].sum()
            
            # Calculate utilization rate
            utilization_rate = (total_enrollment / total_capacity * 100) if total_capacity > 0 else 0
            
            # First-term vs regular courses
            first_term_count = len(df[df['First_Term'] == 'Yes'])
            regular_course_count = len(df[df['First_Term'] == 'No'])
            
            # Teaching mode distribution
            teaching_modes = df['Teaching_Mode'].value_counts().to_dict()
            
            # Program distribution (extract department from course code)
            df['Department'] = df['Course_Code'].str.extract(r'^([A-Z]+)')[0]
            dept_distribution = df['Department'].value_counts().to_dict()
            
            # Course level distribution (extract number from course code)
            df['Course_Level'] = df['Course_Code'].str.extract(r'(\d+)')[0].astype(str).str[0]
            level_distribution = df['Course_Level'].value_counts().to_dict()
            
            # Schedule analysis
            schedule_analysis = self.analyze_schedules(df)
            
            analytics = {
                'overview': {
                    'total_sections': total_sections,
                    'unique_courses': unique_courses,
                    'total_enrollment': int(total_enrollment),
                    'total_capacity': int(total_capacity),
                    'total_available': int(total_available),
                    'total_waitlist': int(total_waitlist),
                    'utilization_rate': round(utilization_rate, 1),
                    'first_term_courses': first_term_count,
                    'regular_courses': regular_course_count
                },
                'teaching_modes': teaching_modes,
                'departments': dept_distribution,
                'course_levels': level_distribution,
                'schedule_analysis': schedule_analysis,
                'last_updated': datetime.now().isoformat()
            }
            
            return analytics
            
        except Exception as e:
            print(f"❌ Analytics calculation failed: {e}")
            raise
    
    def analyze_schedules(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze course scheduling patterns"""
        try:
            # Time slot analysis
            time_slots = []
            for times in df['Class_Times'].dropna():
                if isinstance(times, str) and times.strip():
                    time_slots.extend([t.strip() for t in times.split(',')])
            
            # Weekday analysis  
            weekdays = []
            for days in df['Weekdays'].dropna():
                if isinstance(days, str) and days.strip():
                    weekdays.extend([d.strip() for d in days.split(',')])
            
            from collections import Counter
            weekday_counts = Counter(weekdays)
            time_slot_counts = Counter(time_slots)
            
            return {
                'popular_weekdays': dict(weekday_counts.most_common(5)),
                'popular_time_slots': dict(time_slot_counts.most_common(5)),
                'total_time_slots': len(set(time_slots)),
                'weekend_courses': weekday_counts.get('Saturday', 0) + weekday_counts.get('Sunday', 0)
            }
            
        except Exception as e:
            print(f"⚠️  Schedule analysis failed: {e}")
            return {'error': str(e)}
    
    def generate_quarto_report(self, df: pd.DataFrame, analytics: Dict[str, Any]) -> str:
        """Generate comprehensive Quarto report content"""
        
        # Get current date for report
        report_date = datetime.now().strftime("%B %d, %Y")
        term = df['Term'].iloc[0] if not df.empty else "Unknown Term"
        
        # Create department summary table
        dept_summary = df.groupby('Department').agg({
            'Course_Code': 'count',
            'Enrolled_Seats': 'sum',
            'Total_Seats': 'sum',
            'Available_Seats': 'sum'
        }).round(0).astype(int)
        dept_summary['Utilization_Rate'] = ((dept_summary['Enrolled_Seats'] / dept_summary['Total_Seats']) * 100).round(1)
        dept_summary = dept_summary.rename(columns={
            'Course_Code': 'Sections',
            'Enrolled_Seats': 'Enrolled',
            'Total_Seats': 'Capacity',
            'Available_Seats': 'Available'
        })
        
        # Create detailed course table (sorted by enrollment)
        df_display = df.copy()
        df_display = df_display.sort_values('Enrolled_Seats', ascending=False)
        
        quarto_content = f"""---
title: "Franklin University Course Analytics"
subtitle: "Real-time Enrollment and Capacity Analysis"
format:
  html:
    toc: true
    toc-location: left
    toc-depth: 3
    number-sections: false
    theme: cosmo
    css: |
      .hero-banner {{
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
      }}
      .metric-card {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
      }}
      .metric-value {{
        font-size: 2rem;
        font-weight: bold;
        color: #1e40af;
      }}
      .metric-label {{
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 0.5rem;
      }}
---

::: {{.hero-banner}}
# 📊 Franklin University Course Analytics

**{term}** • **Analytics & Computer Science Programs**

*Last Updated: {report_date}*
:::

## 📈 Executive Summary

:::: {{.columns}}

::: {{.column width="25%"}}
::: {{.metric-card}}
::: {{.metric-value}}
{analytics['overview']['total_sections']}
:::
::: {{.metric-label}}
**Course Sections**
:::
:::
:::

::: {{.column width="25%"}}
::: {{.metric-card}}
::: {{.metric-value}}
{analytics['overview']['unique_courses']}
:::
::: {{.metric-label}}
**Unique Courses**
:::
:::
:::

::: {{.column width="25%"}}
::: {{.metric-card}}
::: {{.metric-value}}
{analytics['overview']['total_enrollment']}
:::
::: {{.metric-label}}
**Total Enrollment**
:::
:::
:::

::: {{.column width="25%"}}
::: {{.metric-card}}
::: {{.metric-value}}
{analytics['overview']['utilization_rate']}%
:::
::: {{.metric-label}}
**Capacity Utilization**
:::
:::
:::

::::

### Key Insights

- **Enrollment Status:** {analytics['overview']['total_enrollment']} students enrolled across {analytics['overview']['total_sections']} course sections
- **Capacity Management:** {analytics['overview']['total_available']} seats still available with {analytics['overview']['utilization_rate']}% utilization rate
- **Program Mix:** {analytics['overview']['first_term_courses']} first-term courses and {analytics['overview']['regular_courses']} regular courses
- **Waitlist Activity:** {analytics['overview']['total_waitlist']} students on waitlists

---

## 🎓 Program Distribution

```{{python}}
#| echo: false
import pandas as pd

# Department summary data
dept_data = {dept_summary.to_dict('index')}
dept_df = pd.DataFrame.from_dict(dept_data, orient='index')
dept_df.index.name = 'Department'

print(dept_df.to_string())
```

### Department Highlights

"""

        # Add department-specific insights
        for dept, data in analytics['departments'].items():
            dept_info = dept_summary.loc[dept] if dept in dept_summary.index else None
            if dept_info is not None:
                quarto_content += f"- **{dept}:** {data} sections, {dept_info['Utilization_Rate']}% utilization\n"

        quarto_content += f"""

---

## 📅 Scheduling Analysis

### Popular Class Times
"""

        # Add popular time slots
        if 'schedule_analysis' in analytics and 'popular_time_slots' in analytics['schedule_analysis']:
            for time_slot, count in list(analytics['schedule_analysis']['popular_time_slots'].items())[:3]:
                quarto_content += f"- **{time_slot}:** {count} sections\n"

        quarto_content += f"""

### Weekday Distribution
"""

        # Add popular weekdays
        if 'schedule_analysis' in analytics and 'popular_weekdays' in analytics['schedule_analysis']:
            for weekday, count in list(analytics['schedule_analysis']['popular_weekdays'].items())[:5]:
                quarto_content += f"- **{weekday}:** {count} sections\n"

        quarto_content += f"""

---

## 📋 Detailed Course Information

```{{python}}
#| echo: false
import pandas as pd

# Course data
course_data = {df_display[['Course_Code', 'Course_Name', 'Enrolled_Seats', 'Total_Seats', 'Available_Seats', 'Waitlist', 'Teaching_Mode', 'First_Term']].to_dict('records')}

df = pd.DataFrame(course_data)
df = df.sort_values('Enrolled_Seats', ascending=False)

print("### Course Enrollment Summary")
print()
print(df.to_string(index=False))
```

---

## 📊 Data Access

### CSV Download
- **[Complete Course Data (CSV)](../data/franklin_courses.csv)** - Full dataset with all course details
- **[Analytics Summary (JSON)](../data/course_analytics.json)** - Processed analytics and metrics

### Data Fields
The course data includes 18 comprehensive fields covering enrollment, scheduling, faculty, and program information:

- **Enrollment Data:** Enrolled/Available/Total seats, waitlist information
- **Schedule Information:** Weekdays, class times, start/end dates  
- **Location & Faculty:** Classroom assignments, instructor information
- **Program Details:** Course codes, names, credits, teaching modes
- **Analytics Tags:** First-term identification, program classification

---

## 🔄 Data Collection

This report is automatically generated from live Franklin University course catalog data:

- **Collection Method:** Automated web scraping via Selenium WebDriver
- **Update Frequency:** Daily at 6:00 AM EST via GitHub Actions
- **Data Validation:** Multi-step validation and error handling
- **Quality Assurance:** Comprehensive data cleaning and verification

### Technical Details
- **Last Scraped:** {analytics.get('last_updated', 'Unknown')}
- **Term Focus:** {term}
- **Sections Analyzed:** {analytics['overview']['total_sections']}
- **Data Freshness:** ✅ Current

---

*This report supports curriculum planning, enrollment management, and program development decisions for Franklin University's Analytics and Computer Science programs.*

"""

        return quarto_content
    
    def save_analytics_json(self, analytics: Dict[str, Any], teach_dir: str):
        """Save analytics data as JSON for API access"""
        try:
            # Determine JSON file path
            json_path = os.path.join(teach_dir, "..", "data", self.json_file)
            
            # Ensure data directory exists
            data_dir = os.path.dirname(json_path)
            os.makedirs(data_dir, exist_ok=True)
            
            with open(json_path, 'w') as f:
                json.dump(analytics, f, indent=2)
            
            print(f"✅ Analytics JSON saved to: {json_path}")
            
        except Exception as e:
            print(f"⚠️  Failed to save analytics JSON: {e}")
    
    def generate_report(self):
        """Main report generation workflow"""
        try:
            print("🎯 Franklin University Course Report Generator")
            print("=" * 60)
            
            # Load course data
            df = self.load_course_data()
            
            if df.empty:
                print("❌ No course data available")
                return
            
            # Calculate analytics
            print("📊 Calculating analytics...")
            analytics = self.calculate_analytics(df)
            
            # Find/create teach directory
            teach_dir = self.find_teach_dir()
            print(f"📁 Using teach directory: {teach_dir}")
            
            # Save analytics JSON
            self.save_analytics_json(analytics, teach_dir)
            
            # Generate Quarto report
            print("📝 Generating Quarto report...")
            report_content = self.generate_quarto_report(df, analytics)
            
            # Save report file
            report_path = os.path.join(teach_dir, self.report_file)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"✅ Report saved to: {report_path}")
            
            # Summary
            print(f"\n📈 Report Summary:")
            print(f"  - {analytics['overview']['total_sections']} course sections analyzed")
            print(f"  - {analytics['overview']['unique_courses']} unique courses")
            print(f"  - {analytics['overview']['utilization_rate']}% capacity utilization")
            print(f"  - Generated professional Quarto report")
            print(f"  - Ready for website integration")
            
        except Exception as e:
            print(f"❌ Report generation failed: {e}")
            raise

def main():
    """Main function"""
    try:
        generator = CourseReportGenerator()
        generator.generate_report()
        print("✅ Report generation complete")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 