#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Franklin University Course Scraper - Data Collection Script

A streamlined data collection script that extracts course information
and outputs clean CSV data for downstream analysis.

Author: Course Analytics Project  
Version: 5.0 (Data Collection Focused)
"""

import time
import os
import re
import csv
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from pathlib import Path
import pandas as pd
import sys

# Compiled regex patterns for better performance
SECTION_PATTERN = re.compile(r'[a-z]+\*\d+-[a-z0-9]{4}', re.IGNORECASE)
COURSE_FORMAT_PATTERN = re.compile(r'^([A-Za-z]+)\s+(\d+)', re.IGNORECASE)
DATE_PATTERN = re.compile(r'\d{1,2}/\d{1,2}/\d{4}')
TIME_PATTERN = re.compile(r'\d{1,2}:\d{2}\s*[AP]M', re.IGNORECASE)

# Weekday mapping for Franklin University formats
WEEKDAY_MAPPING = {
    'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday',
    'R': 'Thursday', 'Th': 'Thursday', 'TH': 'Thursday',
    'F': 'Friday', 'S': 'Saturday', 'U': 'Sunday'
}

# Default values
DEFAULT_CREDITS = '4'
DEFAULT_TOTAL_SEATS = '25'
DEFAULT_WAITLIST = '0'
DEFAULT_LOCATION = 'TBD'
DEFAULT_INSTRUCTOR = 'TBD'
DEFAULT_TIME = 'TBD'
DEFAULT_WEEKDAY = 'TBD'

# Browser settings
BROWSER_WAIT_TIMEOUT = 4.0  # Faster wait for headless mode
INTER_COURSE_DELAY = 1  # Seconds between course scraping

@dataclass
class CourseRequest:
    term: str
    courses: List[Tuple[str, bool]]  # (course_code, is_first_term)

@dataclass  
class CourseSection:
    course_code: str
    session_code: str
    course_name: str
    credits: str
    seats_available: str
    seats_total: str
    seats_waitlisted: str
    weekdays: List[str]
    class_times: List[str]
    locations: List[str]
    instructors: List[str]
    teaching_mode: str
    start_date: str
    end_date: str
    term: str
    is_first_term: bool = False

class FranklinCourseScraper:
    def __init__(self, headless=True):
        self.base_url = "https://selfservice.franklin.edu/Student/Courses/Search"
        self.driver = None
        self.headless = headless
        self.setup_driver()
    
    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
            # Additional options for better headless compatibility
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            if self.headless:
                # Hide automation markers
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.implicitly_wait(2)  # Slightly longer for headless
            mode_text = "headless" if self.headless else "windowed"
            print(f"✅ Chrome driver initialized ({mode_text} mode)")
        except Exception as e:
            print(f"❌ Driver initialization failed: {e}")
            raise

    def read_course_list(self, filename: str = "course_request.md") -> CourseRequest:
        try:
            # Handle path from scripts/ directory or project root
            if not os.path.exists(filename):
                parent_path = os.path.join("..", filename)
                if os.path.exists(parent_path):
                    filename = parent_path
                else:
                    print(f"⚠️  {filename} not found, using default")
                    return CourseRequest("", [("DATA 610", False)])
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse configuration
            config_match = re.search(r'## Current Configuration\s*```\n(.*?)\n```', content, re.DOTALL)
            if not config_match:
                return CourseRequest("", [("DATA 610", False)])
            
            config_block = config_match.group(1)
            lines = [line.strip() for line in config_block.split('\n') if line.strip()]
            
            term = ""
            courses = []
            
            for line in lines:
                if line.startswith('#') or line.startswith('//'):
                    continue
                if line.startswith('Term:'):
                    term = line.replace('Term:', '').strip()
                    continue
                if re.match(r'^[*]?[A-Za-z]+\s+\d+', line):
                    line = line.split('#')[0].strip()
                    is_first_term = line.startswith('*')
                    course_code = line[1:].strip() if is_first_term else line.strip()
                    courses.append((course_code, is_first_term))
            
            if courses:
                print(f"📋 Found {len(courses)} courses for term: {term or 'All terms'}")
                return CourseRequest(term, courses)
            
            return CourseRequest("", [("DATA 610", False)])
            
        except Exception as e:
            print(f"❌ Failed to read {filename}: {e}")
            return CourseRequest("", [("DATA 610", False)])

    def save_to_csv(self, sections: List[CourseSection], filename: str = None):
        try:
            if filename is None:
                # Get the scraper directory (one level up from scripts/) then into data/
                data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
                data_dir = os.path.abspath(data_dir)  # Convert to absolute path
                if not os.path.exists(data_dir):
                    os.makedirs(data_dir, exist_ok=True)
                filename = os.path.join(data_dir, "franklin_courses.csv")
            
            print(f"💾 Saving to {filename}...")
            
            headers = [
                'Course_Code', 'Session_Code', 'Course_Name', 'Credits', 'Term',
                'Enrolled_Seats', 'Total_Seats', 'Waitlist',
                'Weekdays', 'Class_Times', 'Locations', 'Instructors', 
                'Teaching_Mode', 'Start_Date', 'End_Date', 'First_Term', 'Scraped_DateTime'
            ]
            
            # Save timestamp in EST timezone for consistency
            from datetime import timezone, timedelta
            est_tz = timezone(timedelta(hours=-5))  # EST is UTC-5
            scraped_datetime = datetime.now(est_tz).isoformat()
            
            csv_data = []
            for section in sections:
                # Calculate enrolled seats: Enrolled = Total - Available
                enrolled_seats = "N/A"
                try:
                    if (section.seats_total != 'N/A' and section.seats_available != 'N/A' and 
                        str(section.seats_total).isdigit() and str(section.seats_available).isdigit()):
                        enrolled_seats = str(int(section.seats_total) - int(section.seats_available))
                except:
                    pass
                
                row = [
                    section.course_code, section.session_code, section.course_name,
                    section.credits, section.term, enrolled_seats, 
                    section.seats_total, section.seats_waitlisted,
                    ', '.join(section.weekdays), ', '.join(section.class_times),
                    ', '.join(section.locations), ', '.join(section.instructors),
                    section.teaching_mode, section.start_date, section.end_date,
                    'Yes' if section.is_first_term else 'No', scraped_datetime
                ]
                csv_data.append(row)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(csv_data)
            
            print(f"✅ Saved {len(sections)} sections to {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save CSV: {e}")
            raise

    def close(self):
        if self.driver:
            self.driver.quit()

    def search_course(self, course_code: str, term: str) -> bool:
        """Search for course with term filtering"""
        try:
            # Format course code for URL - replace space with + but preserve *
            search_code = course_code.replace(' ', '+')
            if '*' not in search_code:  # Only add * if not already present
                parts = search_code.split('+')
                if len(parts) == 2:
                    search_code = f"{parts[0]}*{parts[1]}"
            
            # Construct search URL without term filtering (like the working reference code)
            search_url = f"{self.base_url}?keyword={search_code}"
            print(f"🔍 Searching: {course_code} (All terms)")
            
            self.driver.get(search_url)
            
            # Wait for page to load and check what we get
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Check if we found results
                page_source = self.driver.page_source
                if "View Available Sections" in page_source:
                    return True
                elif "no results" in page_source.lower():
                    print("⚠️  No courses found")
                    return False
                
                return True
                
            except TimeoutException:
                print("❌ Search page loading timeout")
                return False
            
        except Exception as e:
            print(f"❌ Error during search: {e}")
            return False

    def click_view_sections(self, course_code: str) -> bool:
        """Click view available sections link using the proven working method"""
        try:
            # Always look for the specific course's "View Available Sections" link
            # Don't assume sections are already visible from previous searches
            
            # Format course code for link matching - ensure proper asterisk handling
            search_code = course_code.replace(' ', '-')
            if '*' not in search_code:
                parts = search_code.split('-')
                if len(parts) == 2:
                    search_code = f"{parts[0]}*{parts[1]}"
            
            # Look for "View Available Sections" link with optimized waiting
            selectors = [
                f"//a[contains(text(), 'View Available Sections for {search_code.upper()}')]",
                f"//a[contains(text(), 'View Available Sections for {course_code.upper().replace(' ', '-')}')]",
                f"//a[contains(text(), 'View Available Sections')]",
                "//a[contains(@href, 'sections') or contains(text(), 'sections')]",
                "//button[contains(text(), 'View Available Sections')]",
                "//*[contains(text(), 'View Available Sections')]"
            ]
            
            link_element = None
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        link_element = elements[0]
                        # Check if element is immediately clickable
                        if link_element.is_displayed() and link_element.is_enabled():
                            print(f"✅ Found clickable link: {link_element.text[:50]}...")
                            break
                except:
                    continue
            
            if not link_element:
                print("⚠️  No 'View Available Sections' link found")
                return True
            
            # Enhanced clicking strategy - better for headless mode
            try:
                if self.headless:
                    # For headless mode, try JavaScript click first
                    self.driver.execute_script("arguments[0].scrollIntoView();", link_element)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", link_element)
                    print("✅ Clicked View Available Sections link (JS - headless)")
                else:
                    # For windowed mode, regular click works fine
                    link_element.click()
                    print("✅ Clicked View Available Sections link")
            except:
                # Fallback strategy
                try:
                    self.driver.execute_script("arguments[0].click();", link_element)
                    print("✅ Clicked View Available Sections link (JS fallback)")
                except:
                    print("⚠️ Click failed, continuing anyway")
            
            # Extended wait for content update - headless should be faster
            start_wait = time.time()
            max_wait = BROWSER_WAIT_TIMEOUT if self.headless else 5.0  # Headless should be faster
            
            while time.time() - start_wait < max_wait:
                try:
                    section_tables = self.driver.find_elements(By.CLASS_NAME, "search-sectiontable")
                    term_headers = self.driver.find_elements(By.XPATH, "//h4[contains(text(), 'Spring') or contains(text(), 'Fall') or contains(text(), 'Summer')]")
                    
                    if len(section_tables) > 0 or len(term_headers) > 0:
                        print(f"✅ Content loaded: {len(section_tables)} tables, {len(term_headers)} term headers")
                        return True
                    time.sleep(0.2)  # Check every 200ms
                except:
                    time.sleep(0.2)
            
            print("⚠️  Timeout waiting for sections to load, continuing anyway")
            return True
            
        except Exception as e:
            print(f"❌ Failed to click section link: {e}")
            return False

    def extract_course_info(self, course_code: str, term: str) -> List[CourseSection]:
        """Extract detailed course information using the proven working method"""
        try:
            # Remove asterisk for course info extraction
            display_code = course_code.replace('*', ' ').strip()
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            sections = []
            
            course_info = self.extract_basic_course_info(soup, display_code)
            
            term_headers = soup.find_all('h4', string=lambda t: t and any(term_word in t for term_word in ['Spring', 'Summer', 'Fall', 'Winter']) and '20' in t)
            
            # Debug: Show what terms are actually available
            print(f"🔍 Found {len(term_headers)} total term headers:")
            for i, h in enumerate(term_headers[:3]):  # Show first 3
                print(f"   {i+1}. '{h.get_text(strip=True)}'")
            
            # Filter to only the specified term during extraction (not search)
            if term:
                original_count = len(term_headers)
                term_headers = [h for h in term_headers if term in h.get_text(strip=True)]
                print(f"🔍 Filtered from {original_count} to {len(term_headers)} headers for {term}")
            else:
                print(f"🔍 Using all {len(term_headers)} term headers")
            
            for term_header in term_headers:
                term_text = term_header.get_text(strip=True)
                term_sections = self.extract_sections_for_term(soup, term_header, term_text, course_info, course_code)
                sections.extend(term_sections)
            
            # Filter to keep FF sections OR sections with "hybrid" in locations
            filtered_sections = []
            for section in sections:
                # Keep if has FF in session code (and not WW)
                if "FF" in section.session_code and "WW" not in section.session_code:
                    filtered_sections.append(section)
                # Also keep if has "hybrid" in locations (case insensitive)
                elif any("hybrid" in location.lower() for location in section.locations):
                    filtered_sections.append(section)
            
            # Deduplicate sections based on course_code + session_code
            unique_sections = {}
            for section in filtered_sections:
                key = f"{section.course_code}_{section.session_code}"
                if key not in unique_sections:
                    unique_sections[key] = section
            
            print(f"✅ Extracted {len(unique_sections)} sections for {course_code}")
            return list(unique_sections.values())
            
        except Exception as e:
            print(f"❌ Course information extraction failed: {e}")
            return []

    def extract_basic_course_info(self, soup, course_name):
        """Extract basic course information"""
        course_info = {
            'title': f"{course_name} Course",
            'credits': '4',
            'description': '',
            'prerequisites': ''
        }
        
        # Clean course name for matching
        clean_name = course_name.replace('*', ' ').strip()
        parts = clean_name.split()
        if len(parts) >= 2:
            dept = parts[0].upper()
            num = parts[1]
            patterns = [
                lambda t: t and f"{dept}-{num}" in t.upper() and 'Credits' in t,
                lambda t: t and f"{dept} {num}" in t.upper() and 'Credits' in t,
                lambda t: t and f"{dept}*{num}" in t.upper() and 'Credits' in t,
                lambda t: t and dept in t.upper() and num in t and 'Credits' in t
            ]
            
            for pattern in patterns:
                title_elem = soup.find('span', string=pattern)
                if title_elem:
                    full_title = title_elem.get_text(strip=True)
                    # Clean the title to remove credit information
                    if '(' in full_title and 'Credits' in full_title:
                        course_info['title'] = full_title.split('(')[0].strip()
                        # Extract credits number from format like "(0 Credits)" or "(4 Credits)"
                        credits_match = re.search(r'\((\d+)\s+Credits?\)', full_title)
                        if credits_match:
                            course_info['credits'] = credits_match.group(1)
                    else:
                        course_info['title'] = full_title
                    break
        
        return course_info

    def extract_sections_for_term(self, soup, term_header, term_text, course_info, course_name):
        """Extract all sections for a specific term using the proven working method"""
        sections = []
        
        print(f"🔍 Looking for sections under '{term_text}' header...")
        
        # Find all section links after this term header
        current_element = term_header
        element_count = 0
        while current_element and element_count < 50:  # Safety limit
            current_element = current_element.find_next_sibling()
            element_count += 1
            
            if not current_element:
                break
            
            # Stop if we hit another term header
            if current_element.name == 'h4' and any(
                term_word in current_element.get_text() 
                for term_word in ['Spring', 'Summer', 'Fall', 'Winter']
            ):
                print(f"🔍 Stopping at next term header: {current_element.get_text()}")
                break
            
            # Look for section links
            section_links = current_element.find_all('a', href=True) if hasattr(current_element, 'find_all') else []
            
            if section_links:
                print(f"🔍 Found {len(section_links)} links in element {element_count}")
                for i, link in enumerate(section_links):
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)
                    print(f"   Link {i+1}: '{link_text}' -> {href}")
                    
                    # Be more flexible with link detection - look for any link that might be a section
                    # Check for section patterns: any 4 characters after a dash (more general approach)
                    is_section_link = (
                        SECTION_PATTERN.search(href) or 
                        SECTION_PATTERN.search(link_text) or
                        'section' in href.lower() or 
                        'section' in link_text.lower()
                    )
                    
                    if is_section_link:
                        print(f"   ✅ Processing section link: {link_text}")
                        section = self.extract_section_details(link, soup, term_text, course_info)
                        if section:
                            sections.append(section)
                            print(f"   ✅ Successfully extracted section: {section.session_code}")
                        else:
                            print(f"   ❌ Failed to extract section details")
            
            # Also look for section tables directly
            section_tables = current_element.find_all('table', class_='search-sectiontable') if hasattr(current_element, 'find_all') else []
            if section_tables:
                print(f"🔍 Found {len(section_tables)} section tables in element {element_count}")
        
        print(f"🔍 Total sections found for {term_text}: {len(sections)}")
        return sections

    def extract_section_details(self, link_elem, soup, term, course_info) -> Optional[CourseSection]:
        """Extract detailed information for a single section using the proven working method"""
        try:
            # Get session code from link text
            link_text = link_elem.get_text(strip=True)
            session_code = link_text.split()[-1] if link_text else "Unknown"
            
            # Find the section table
            section_table = link_elem.find_next('table', class_='search-sectiontable')
            if not section_table:
                return None
            
            # Extract seat information (enrolled/total/waitlist pattern)
            seats_info = self.extract_seats_info(section_table)
            
            # Extract time and location information
            time_info = self.extract_time_info(section_table)
            location_info = self.extract_locations(section_table)
            instructor_info = self.extract_instructor_info(section_table)
            date_info = self.extract_date_info(section_table)
            
            # Parse weekdays into both full and short forms
            weekdays_full = time_info.get('weekdays', ['TBD'])
            weekdays_short = [self.convert_to_short_weekday(day) for day in weekdays_full]
            
            # Create section object with all the extracted data
            section = CourseSection(
                course_code=course_info.get('title', 'Unknown').split()[0] + '*' + course_info.get('title', 'Unknown').split()[1] if len(course_info.get('title', '').split()) >= 2 else 'Unknown*Course',
                session_code=session_code,
                course_name=course_info.get('title', 'Unknown Course'),
                credits=course_info.get('credits', DEFAULT_CREDITS),
                seats_available=seats_info.get('available', '0'),
                seats_total=seats_info.get('total', '25'),
                seats_waitlisted=seats_info.get('waitlist', '0'),
                weekdays=weekdays_full,
                class_times=time_info.get('times', ['TBD']),
                locations=location_info,
                instructors=instructor_info,
                teaching_mode=self.determine_teaching_mode(location_info),
                start_date=date_info.get('start', '01/15/2025'),
                end_date=date_info.get('end', '03/15/2025'),
                term=term
            )
            
            return section
            
        except Exception as e:
            print(f"❌ Failed to extract section details: {e}")
            return None

    def convert_to_short_weekday(self, full_day):
        """Convert full weekday name to short form"""
        mapping = {
            'Monday': 'Mon', 'Tuesday': 'Tue', 'Wednesday': 'Wed',
            'Thursday': 'Thu', 'Friday': 'Fri', 'Saturday': 'Sat', 'Sunday': 'Sun'
        }
        return mapping.get(full_day, full_day)

    def extract_seats_info(self, table):
        """Extract seat availability information - Franklin format: Available/Total/Waitlisted"""
        seats_info = {'available': DEFAULT_WAITLIST, 'total': DEFAULT_TOTAL_SEATS, 'waitlist': DEFAULT_WAITLIST}
        
        try:
            # Look for specific seat info span first (like reference code)
            seat_span = table.find('span', class_='search-seatsavailabletext')
            if seat_span:
                seat_text = seat_span.get_text(strip=True)
                if '/' in seat_text:
                    parts = seat_text.split('/')
                    if len(parts) >= 3:
                        seats_info['available'] = parts[0].strip()
                        seats_info['total'] = parts[1].strip()
                        seats_info['waitlist'] = parts[2].strip()
                        return seats_info
            
            # Fallback: Look for seat information in general table cells
            cells = table.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text(strip=True)
                
                # Pattern: "20 / 20 / 0" (Available/Total/Waitlisted)
                if '/' in text and any(char.isdigit() for char in text):
                    parts = [p.strip() for p in text.split('/')]
                    if len(parts) >= 3:
                        seats_info = {
                            'available': parts[0] if parts[0].isdigit() else DEFAULT_WAITLIST,
                            'total': parts[1] if parts[1].isdigit() else DEFAULT_TOTAL_SEATS,
                            'waitlist': parts[2] if parts[2].isdigit() else DEFAULT_WAITLIST
                        }
                        break
        except:
            pass
        
        return seats_info

    def extract_time_info(self, table):
        """Extract schedule time information"""
        time_info = {'weekdays': [DEFAULT_WEEKDAY], 'times': [DEFAULT_TIME]}
        
        try:
            cells = table.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text(strip=True)
                
                # Look for time patterns like "6:00 PM - 8:00 PM"
                if TIME_PATTERN.search(text):
                    time_info['times'] = [text]
                
                # Look for weekday patterns like "MW" or "Monday, Wednesday"
                weekday_patterns = ['M', 'T', 'W', 'R', 'F', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                if any(pattern in text for pattern in weekday_patterns):
                    weekdays = self.parse_weekdays(text)
                    if weekdays:
                        time_info['weekdays'] = weekdays
        except:
            pass
        
        return time_info

    def parse_weekdays(self, text):
        """Parse weekday abbreviations into full names"""
        weekdays = []
        
        # Handle compact format like "MW", "TR", etc.
        if len(text) <= 4 and all(c in 'MTWRFSU' for c in text.upper()):
            for char in text.upper():
                if char in WEEKDAY_MAPPING:
                    weekdays.append(WEEKDAY_MAPPING[char])
        
        # Handle comma-separated format
        elif ',' in text:
            for day in text.split(','):
                day = day.strip()
                if day in WEEKDAY_MAPPING.values():
                    weekdays.append(day)
        
        return weekdays if weekdays else [DEFAULT_WEEKDAY]

    def extract_locations(self, table):
        """Extract location information"""
        locations = [DEFAULT_LOCATION]
        
        try:
            cells = table.find_all(['td', 'th'])
            for cell in cells:
                text = cell.get_text(strip=True)
                
                # Look for room/building patterns
                if any(keyword in text.lower() for keyword in ['room', 'building', 'hall', 'downtown', 'campus']):
                    locations = [text]
                    break
        except:
            pass
        
        return locations

    def extract_instructor_info(self, table):
        """Extract instructor information"""
        instructors = [DEFAULT_INSTRUCTOR]
        
        try:
            # Look for instructor names in multiple ways
            cells = table.find_all(['td', 'th'])
            candidate_instructors = []
            
            for cell in cells:
                text = cell.get_text(strip=True)
                
                # Skip if text is too short or contains excluded keywords
                if (len(text) < 4 or
                    any(keyword in text.lower() for keyword in [
                        'room', 'time', 'pm', 'am', 'seats', 'enrolled', 'available', 
                        'total', 'waitlist', 'downtown', 'building', 'hall', 'campus',
                        'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                        'saturday', 'sunday', 'face-to-face', 'hybrid', 'online',
                        DEFAULT_INSTRUCTOR.lower(), 'course', 'section', 'credit',
                        'start', 'end', 'date', 'week', 'class', 'meeting'
                    ])):
                    continue
                
                # Look for instructor patterns
                # Pattern 1: Names with space and alphabetic characters
                if (' ' in text and 
                    any(c.isalpha() for c in text) and 
                    not text.replace(' ', '').replace(',', '').replace('.', '').isdigit()):
                    
                    # Additional check: should have at least one capital letter (typical for names)
                    if any(c.isupper() for c in text):
                        candidate_instructors.append(text)
                
                # Pattern 2: Names with comma (Last, First format)
                elif (',' in text and 
                      any(c.isalpha() for c in text) and 
                      len(text.split(',')) == 2):
                    candidate_instructors.append(text)
            
            # If we found candidates, use the first reasonable one
            if candidate_instructors:
                # Prefer names that look more like "First Last" or "Last, First"
                for candidate in candidate_instructors:
                    # Skip if it looks like a course code or contains numbers prominently
                    if not re.search(r'\d{3,}', candidate):  # No 3+ digit numbers
                        instructors = [candidate]
                        break
                else:
                    # Fall back to first candidate if none look ideal
                    instructors = [candidate_instructors[0]]
                    
        except Exception as e:
            print(f"Debug: Instructor extraction error: {e}")
            pass
        
        return instructors

    def extract_date_info(self, table):
        """Extract start and end dates"""
        date_info = {'start': 'N/A', 'end': 'N/A'}
        
        try:
            # Look for date spans like in reference code
            date_spans = table.find_all('span', class_='search-meetingtimestext')
            
            for span in date_spans:
                text = span.get_text(strip=True)
                # Look for proper date pattern: MM/DD/YYYY - MM/DD/YYYY
                if re.match(r'\d{1,2}/\d{1,2}/\d{4}\s*-\s*\d{1,2}/\d{1,2}/\d{4}', text):
                    dates = text.split('-')
                    if len(dates) == 2:
                        date_info['start'] = dates[0].strip()
                        date_info['end'] = dates[1].strip()
                    break
        except:
            pass
        
        return date_info

    def determine_teaching_mode(self, locations):
        """Determine teaching mode based on location"""
        location_text = ' '.join(locations).lower()
        
        if 'online' in location_text or 'virtual' in location_text:
            return 'Online'
        elif 'hybrid' in location_text:
            return 'Hybrid'
        else:
            return 'Face-to-Face'

    def scrape_course(self, course_code: str, term: str) -> List[CourseSection]:
        """Scrape a single course and return its sections"""
        try:
            print(f"🎯 Scraping {course_code}...")
            
            # Format course code consistently (like the reference code)
            formatted_code = course_code
            if '*' not in formatted_code:
                match = COURSE_FORMAT_PATTERN.match(formatted_code)
                if match:
                    formatted_code = f"{match.group(1)}*{match.group(2)}"
            
            # Always do a fresh search for each course (like the reference code)
            if not self.search_course(formatted_code, term):
                print(f"❌ Failed to search for {course_code}")
                return []
            
            # Click view sections for this specific course
            if not self.click_view_sections(formatted_code):
                print(f"❌ Failed to view sections for {course_code}")
                return []
            
            # Extract course information
            sections = self.extract_course_info(formatted_code, term)
            
            if sections:
                print(f"✅ Found {len(sections)} sections for {course_code}")
            else:
                print(f"⚠️  No sections found for {course_code}")
            
            return sections
            
        except Exception as e:
            print(f"❌ Error scraping {course_code}: {e}")
            return []

    def scrape_multiple_courses(self, course_request: CourseRequest) -> List[CourseSection]:
        """Scrape multiple courses and return all sections"""
        all_sections = []
        
        try:
            print(f"🎯 Starting to scrape {len(course_request.courses)} courses...")
            
            for i, (course_code, is_first_term) in enumerate(course_request.courses, 1):
                print(f"\n📚 Course {i}/{len(course_request.courses)}: {course_code}")
                
                sections = self.scrape_course(course_code, course_request.term)
                
                # Mark first-term courses
                for section in sections:
                    section.is_first_term = is_first_term
                
                all_sections.extend(sections)
                
                # Brief pause between courses to be respectful
                if i < len(course_request.courses):
                    time.sleep(INTER_COURSE_DELAY)
            
            print(f"\n✅ Scraping complete: {len(all_sections)} total sections found")
            return all_sections
            
        except Exception as e:
            print(f"❌ Multi-course scraping failed: {e}")
            return all_sections

def main():
    scraper = None
    try:
        print("🎯 Franklin University Course Scraper - Data Collection")
        print("=" * 60)
        
        scraper = FranklinCourseScraper(headless=True)
        course_request = scraper.read_course_list("course_request.md")
        
        if not course_request.courses:
            print("❌ No courses to process")
            return
        
        # Actually scrape the courses
        print("🌐 Starting web scraping...")
        sections = scraper.scrape_multiple_courses(course_request)
        
        if sections:
            scraper.save_to_csv(sections)
            print("✅ Data collection complete")
        else:
            print("❌ No data collected")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main() 