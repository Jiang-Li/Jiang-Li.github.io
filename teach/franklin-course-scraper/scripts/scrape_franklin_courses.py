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
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
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
BROWSER_WAIT_TIMEOUT = 10.0  # Increased timeout to handle slow-loading courses
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
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
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
        """Read course list configuration - supports single or multiple terms"""
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
            
            # Parse configuration - match text between ## Current Configuration and closing ```
            # Skip past the Example section by looking for the configuration that comes AFTER it
            config_match = re.search(r'## Current Configuration\s*\n\s*```[^\n]*\n(.*?)\n```', content, re.DOTALL)
            if not config_match:
                return CourseRequest("", [("DATA 610", False)])
            
            config_block = config_match.group(1)
            lines = [line.strip() for line in config_block.split('\n') if line.strip()]
            
            term = ""
            courses = []
            
            for line in lines:
                if line.startswith('#') or line.startswith('//'):
                    continue
                # Skip separator lines
                if line.startswith('---'):
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
    
    def read_multi_term_course_list(self, filename: str = "course_request.md") -> List[CourseRequest]:
        """Read multiple term configurations from a single file"""
        try:
            # Handle path from scripts/ directory or project root
            if not os.path.exists(filename):
                parent_path = os.path.join("..", filename)
                if os.path.exists(parent_path):
                    filename = parent_path
                else:
                    print(f"⚠️  {filename} not found, using default")
                    return [CourseRequest("", [("DATA 610", False)])]
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse configuration
            config_match = re.search(r'## Current Configuration\s*```\n(.*?)\n```', content, re.DOTALL)
            if not config_match:
                return [CourseRequest("", [("DATA 610", False)])]
            
            config_block = config_match.group(1)
            lines = [line.strip() for line in config_block.split('\n') if line.strip()]
            
            course_requests = []
            current_term = ""
            current_courses = []
            
            for line in lines:
                if line.startswith('#') or line.startswith('//'):
                    continue
                if line.startswith('---'):
                    # Separator: save current term and start new one
                    if current_term and current_courses:
                        course_requests.append(CourseRequest(current_term, current_courses))
                        print(f"📋 Found {len(current_courses)} courses for term: {current_term}")
                    current_term = ""
                    current_courses = []
                    continue
                if line.startswith('Term:'):
                    # Save previous term if exists
                    if current_term and current_courses:
                        course_requests.append(CourseRequest(current_term, current_courses))
                        print(f"📋 Found {len(current_courses)} courses for term: {current_term}")
                    current_term = line.replace('Term:', '').strip()
                    current_courses = []
                    continue
                if re.match(r'^[*]?[A-Za-z]+\s+\d+', line):
                    line = line.split('#')[0].strip()
                    is_first_term = line.startswith('*')
                    course_code = line[1:].strip() if is_first_term else line.strip()
                    current_courses.append((course_code, is_first_term))
            
            # Save the last term
            if current_term and current_courses:
                course_requests.append(CourseRequest(current_term, current_courses))
                print(f"📋 Found {len(current_courses)} courses for term: {current_term}")
            
            if not course_requests:
                return [CourseRequest("", [("DATA 610", False)])]
            
            return course_requests
            
        except Exception as e:
            print(f"❌ Failed to read {filename}: {e}")
            return [CourseRequest("", [("DATA 610", False)])]

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
            
            # Group sections by course code to combine multiple sections
            from collections import defaultdict
            grouped_sections = defaultdict(list)
            for section in sections:
                # Use the base course code (without session) as grouping key
                base_course_code = section.course_code.split('*')[0] + '*' + section.course_code.split('*')[1] if '*' in section.course_code else section.course_code
                grouped_sections[base_course_code].append(section)
            
            csv_data = []
            for course_code, course_sections in grouped_sections.items():
                # If only one section, use simple format without semicolons
                if len(course_sections) == 1:
                    section = course_sections[0]
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
                
                else:
                    # Multiple sections - combine with semicolons
                    first_section = course_sections[0]
                    
                    # Combine session codes
                    all_session_codes = [section.session_code for section in course_sections]
                    combined_session_code = '; '.join(all_session_codes)
                    
                    # Combine and calculate total enrolled seats
                    total_enrolled = 0
                    total_capacity = 0
                    total_waitlist = 0
                    
                    for section in course_sections:
                        try:
                            if (section.seats_total != 'N/A' and section.seats_available != 'N/A' and 
                                str(section.seats_total).isdigit() and str(section.seats_available).isdigit()):
                                enrolled = int(section.seats_total) - int(section.seats_available)
                                total_enrolled += enrolled
                                total_capacity += int(section.seats_total)
                            if section.seats_waitlisted != 'N/A' and str(section.seats_waitlisted).isdigit():
                                total_waitlist += int(section.seats_waitlisted)
                        except:
                            pass
                    
                    # Combine weekdays, times, locations, instructors with semicolons
                    all_weekdays = []
                    all_times = []
                    all_locations = []
                    all_instructors = []
                    all_modes = []
                    all_start_dates = []
                    all_end_dates = []
                    
                    for section in course_sections:
                        # Flatten lists and add to combined lists
                        if section.weekdays and section.weekdays != ['TBD']:
                            all_weekdays.extend(section.weekdays)
                        if section.class_times and section.class_times != ['TBD']:
                            all_times.extend(section.class_times)
                        if section.locations:
                            all_locations.extend(section.locations)
                        if section.instructors:
                            all_instructors.extend(section.instructors)
                        if section.teaching_mode:
                            all_modes.append(section.teaching_mode)
                        if section.start_date and section.start_date != 'N/A':
                            all_start_dates.append(section.start_date)
                        if section.end_date and section.end_date != 'N/A':
                            all_end_dates.append(section.end_date)
                    
                    # Join with semicolons and remove duplicates
                    combined_weekdays = '; '.join(list(dict.fromkeys(all_weekdays))) if all_weekdays else 'TBD'
                    combined_times = '; '.join(list(dict.fromkeys(all_times))) if all_times else 'TBD'
                    combined_locations = '; '.join(list(dict.fromkeys(all_locations))) if all_locations else 'TBD'
                    combined_instructors = '; '.join(list(dict.fromkeys(all_instructors))) if all_instructors else 'TBD'
                    combined_modes = '; '.join(list(dict.fromkeys(all_modes))) if all_modes else 'TBD'
                    combined_start_dates = '; '.join(list(dict.fromkeys(all_start_dates))) if all_start_dates else 'N/A'
                    combined_end_dates = '; '.join(list(dict.fromkeys(all_end_dates))) if all_end_dates else 'N/A'
                    
                    row = [
                        first_section.course_code, combined_session_code, first_section.course_name,
                        first_section.credits, first_section.term, 
                        str(total_enrolled) if total_enrolled > 0 else "N/A",
                        str(total_capacity) if total_capacity > 0 else "N/A", 
                        str(total_waitlist) if total_waitlist > 0 else "0",
                        combined_weekdays, combined_times, combined_locations, combined_instructors,
                        combined_modes, combined_start_dates, combined_end_dates,
                        'Yes' if first_section.is_first_term else 'No', scraped_datetime
                    ]
                    csv_data.append(row)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(csv_data)
            
            print(f"✅ Saved {len(csv_data)} courses (from {len(sections)} sections) to {filename}")
            
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
            print(f"🔍 Term parameter received: '{term}'")
            if term:
                original_count = len(term_headers)
                term_headers = [h for h in term_headers if term in h.get_text(strip=True)]
                print(f"🔍 Filtered from {original_count} to {len(term_headers)} headers for '{term}'")
            else:
                print(f"🔍 Using all {len(term_headers)} term headers (term parameter is empty)")
            
            for term_header in term_headers:
                term_text = term_header.get_text(strip=True)
                term_sections = self.extract_sections_for_term(soup, term_header, term_text, course_info, course_code)
                sections.extend(term_sections)
            
            # Simplified filtering: Only keep FF (face-to-face) sections
            filtered_sections = []
            for section in sections:
                # Only keep FF sections (face-to-face)
                if "FF" in section.session_code:
                    filtered_sections.append(section)
                    print(f"   ✅ Keeping FF section: {section.session_code}")
                else:
                    print(f"   ❌ Filtering out non-FF section: {section.session_code}")
            
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
            
            print(f"   🔍 Extracting details for section: {session_code}")
            
            # Find the section table
            section_table = link_elem.find_next('table', class_='search-sectiontable')
            if not section_table:
                print(f"   ❌ No section table found for {session_code}")
                return None
            
            # Extract seat information (enrolled/total/waitlist pattern)
            seats_info = self.extract_seats_info(section_table)
            
            # Extract time and location information
            time_info = self.extract_time_info(section_table)
            location_info = self.extract_locations(section_table)
            instructor_info = self.extract_instructor_info(section_table)
            date_info = self.extract_date_info(section_table)
            
            # Debug: Print extracted data for each section
            print(f"   📊 {session_code} - Times: {time_info.get('times', ['TBD'])}")
            print(f"   📍 {session_code} - Locations: {location_info}")
            print(f"   🎯 {session_code} - Weekdays: {time_info.get('weekdays', ['TBD'])}")
            
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
        """Extract schedule time information - enhanced for both FF and WW sections"""
        time_info = {'weekdays': [DEFAULT_WEEKDAY], 'times': [DEFAULT_TIME]}
        
        try:
            # Get all text content from the table
            all_text = table.get_text(' ', strip=True)
            
            # Look for various time patterns (more comprehensive)
            import re
            
            # Pattern 1: Standard time format "6:00 PM - 8:00 PM"
            time_patterns = [
                r'(\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M)',
                r'(\d{1,2}:\d{2}[AP]M\s*-\s*\d{1,2}:\d{2}[AP]M)',
                r'(\d{1,2}:\d{2}\s*[ap]m\s*-\s*\d{1,2}:\d{2}\s*[ap]m)',
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                if matches:
                    time_info['times'] = matches
                    break
            
            # Enhanced extraction for weekday+time pairs (like "T 6:00 PM", "Th 10:00 AM")
            weekday_time_pairs = []
            
            # First, check for slash-separated weekdays with single time (like "T/Th 10:00 AM - 12:00 PM")
            slash_pattern = r'\b(T/Th|M/W|W/F|M/W/F)\s+(\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M)'
            slash_matches = re.finditer(slash_pattern, all_text, re.IGNORECASE)
            
            all_weekdays = []
            all_times = []
            
            for match in slash_matches:
                weekday_pattern = match.group(1)
                time_range = match.group(2).strip()
                
                # Parse the slash-separated weekdays
                parsed_weekdays = self.parse_weekdays(weekday_pattern)
                
                if parsed_weekdays and parsed_weekdays != [DEFAULT_WEEKDAY]:
                    all_weekdays.extend(parsed_weekdays)
                    # Duplicate the time for each weekday
                    for weekday in parsed_weekdays:
                        all_times.append(time_range)
                        weekday_time_pairs.append((weekday, time_range))
            
            # If no slash patterns found, look for individual weekday+time patterns
            if not weekday_time_pairs:
                # Combined pattern to find all weekday+time pairs in order
                combined_pattern = r'\b(Th|T|M|W|F|S|U|Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+(\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M)'
                
                # Find all matches in order of appearance in text
                matches = re.finditer(combined_pattern, all_text, re.IGNORECASE)
                for match in matches:
                    weekday_abbrev = match.group(1)
                    time_range = match.group(2)
                    
                    # Special handling for T vs Th distinction
                    if weekday_abbrev.upper() == 'T':
                        # Check if this T is actually part of Th by looking at the next character
                        start_pos = match.start(1)
                        if (start_pos + 1 < len(all_text) and 
                            all_text[start_pos:start_pos+2].upper() == 'TH'):
                            continue  # Skip this T as it's part of Th
                        parsed_weekdays = ['Tuesday']
                    elif weekday_abbrev.upper() == 'TH':
                        parsed_weekdays = ['Thursday']
                    else:
                        parsed_weekdays = self.parse_weekdays(weekday_abbrev)
                    
                    if parsed_weekdays and parsed_weekdays != [DEFAULT_WEEKDAY]:
                        all_weekdays.extend(parsed_weekdays)
                        all_times.append(time_range.strip())
                        weekday_time_pairs.append((parsed_weekdays[0], time_range.strip()))
            
            # If we found weekday+time pairs, use them
            if weekday_time_pairs:
                time_info['weekdays'] = all_weekdays
                time_info['times'] = all_times
            else:
                # Fallback to original method for bulk patterns (with/without slash)
                weekday_patterns = [
                    r'\b(T/Th)\b',  # Specific pattern for T/Th (highest priority)
                    r'\b(M/W/F|M/W|W/F|T/Th)\b',  # Common slash-separated patterns (removed Th/F)
                    r'\b(Th)\b',  # Specific pattern for Thursday (higher priority than T)
                    r'\b(T)\b',   # Specific pattern for Tuesday  
                    r'\b([MTWFSU]{1,5})\b',  # Compact format like MW (removed R)
                    r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b',
                    r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b'
                ]
                
                for pattern in weekday_patterns:
                    matches = re.findall(pattern, all_text, re.IGNORECASE)
                    if matches:
                        # Convert matches to standard weekdays
                        weekdays = []
                        for match in matches:
                            parsed = self.parse_weekdays(match)
                            weekdays.extend(parsed)
                        
                        if weekdays and weekdays != [DEFAULT_WEEKDAY]:
                            time_info['weekdays'] = list(set(weekdays))  # Remove duplicates
                            # For fallback patterns with slash separation, duplicate times
                            if time_info['times'] != [DEFAULT_TIME] and '/' in matches[0]:
                                # Duplicate the times for each weekday
                                original_times = time_info['times'][:]
                                time_info['times'] = original_times * len(weekdays)
                            break
            
            # Alternative: Look in individual cells (original method as fallback)
            if time_info['times'] == [DEFAULT_TIME]:
                cells = table.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    
                    # Look for time patterns
                    for pattern in time_patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            time_info['times'] = [text]
                            break
                    
                    if time_info['times'] != [DEFAULT_TIME]:
                        break
        
        except Exception as e:
            print(f"   ⚠️  Time extraction error: {e}")
            pass
        
        return time_info

    def parse_weekdays(self, text):
        """Parse weekday abbreviations into full names - enhanced"""
        weekdays = []
        text = text.strip()
        
        # Enhanced weekday mapping with T vs Th distinction (no R for Thursday - Franklin uses Th)
        weekday_mapping = {
            'M': 'Monday', 'T': 'Tuesday', 'W': 'Wednesday', 'TH': 'Thursday',
            'F': 'Friday', 'S': 'Saturday', 'U': 'Sunday',
            'MON': 'Monday', 'TUE': 'Tuesday', 'WED': 'Wednesday', 'THU': 'Thursday',
            'FRI': 'Friday', 'SAT': 'Saturday', 'SUN': 'Sunday',
            'MONDAY': 'Monday', 'TUESDAY': 'Tuesday', 'WEDNESDAY': 'Wednesday', 
            'THURSDAY': 'Thursday', 'FRIDAY': 'Friday', 'SATURDAY': 'Saturday', 'SUNDAY': 'Sunday'
        }
        
        # Handle direct mapping with special case for T vs Th
        text_upper = text.upper()
        
        # Special handling for T vs Th
        if text_upper == 'TH':
            return ['Thursday']
        elif text_upper == 'T':
            return ['Tuesday']
        elif text_upper in weekday_mapping:
            return [weekday_mapping[text_upper]]
        
        # Handle compact format like "MW", "MTh", etc. (no R - Franklin uses Th for Thursday)
        if len(text) <= 5 and all(c in 'MTWFSHUT' for c in text.upper()):
            text_upper = text.upper()
            i = 0
            while i < len(text_upper):
                # Check for "TH" first (two characters) - highest priority
                if i < len(text_upper) - 1 and text_upper[i:i+2] == 'TH':
                    weekdays.append('Thursday')
                    i += 2
                # Check for single "T" (Tuesday) - make sure it's not part of "TH"
                elif text_upper[i] == 'T' and (i == len(text_upper) - 1 or text_upper[i+1] != 'H'):
                    weekdays.append('Tuesday')
                    i += 1
                # Check for other single character weekdays
                elif text_upper[i] in weekday_mapping and text_upper[i] != 'T':
                    weekdays.append(weekday_mapping[text_upper[i]])
                    i += 1
                else:
                    i += 1
        
        # Handle separated format (comma, space, slash)
        elif any(sep in text for sep in [',', ' ', '/']):
            separators = [',', ' ', '/']
            for sep in separators:
                if sep in text:
                    for day in text.split(sep):
                        day = day.strip().upper()
                        # Handle "TH" specifically for Thursday
                        if day == 'TH':
                            weekdays.append('Thursday')
                        elif day == 'T':
                            weekdays.append('Tuesday')
                        elif day in weekday_mapping:
                            weekdays.append(weekday_mapping[day])
                    break
        
        # Handle full weekday names in text
        else:
            import re
            for abbrev, full_name in weekday_mapping.items():
                if re.search(r'\b' + re.escape(abbrev) + r'\b', text_upper):
                    weekdays.append(full_name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_weekdays = []
        for day in weekdays:
            if day not in seen:
                seen.add(day)
                unique_weekdays.append(day)
        
        return unique_weekdays if unique_weekdays else [DEFAULT_WEEKDAY]

    def extract_locations(self, table):
        """Extract location information - enhanced to capture multiple location components"""
        locations = []
        
        try:
            # Get all text content from the table
            all_text = table.get_text(' ', strip=True)
            print(f"   🔍 Full location text: {repr(all_text[:200])}")
            
            # Enhanced location patterns - most specific first
            import re
            
            location_patterns = [
                # Specific room patterns (highest priority)
                r'(Frasch\s+Hall\s+\d+)',
                r'([A-Za-z]+\s+Hall\s+\d+)',
                r'([A-Za-z]+\s+Building\s+\d+)',
                r'(Room\s+\d+)',
                r'(Classroom\s+\d+)',
                # General location patterns
                r'(Downtown[^,]*(?:Hall|Room|Building|Class)[^,]*\d+)',
                r'(Internet\s+Class[^,]*)',
                r'(Online[^,]*)',
                # Blended course patterns - capture classroom info near lecture times
                r'(LEC\s+[MTWRFSU]\s+\d{1,2}:\d{2}\s*[AP]M[^,]*(?:Hall|Room|Building)[^,]*\d+)',
                r'((?:Hall|Room|Building)[^,]*\d+[^,]*LEC\s+[MTWRFSU])',
            ]
            
            # Try each pattern and collect all unique matches
            found_locations = []
            for pattern in location_patterns:
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                for match in matches:
                    clean_match = re.sub(r'\s+', ' ', match.strip())
                    if clean_match and clean_match not in found_locations:
                        found_locations.append(clean_match)
            
            # For blended courses, also search for classroom info more broadly
            if 'blended' in all_text.lower() or 'lec' in all_text.lower():
                # Look for standalone building/room numbers that might be missed
                additional_patterns = [
                    r'(\b(?:Frasch|Main|North|South|East|West)\s+(?:Hall|Building)\s+\d+\b)',
                    r'(\bRoom\s+\d+\b)',
                    r'(\b[A-Z][a-z]+\s+\d{3,4}\b)',  # Building + room number like "Frasch 422"
                ]
                
                for pattern in additional_patterns:
                    matches = re.findall(pattern, all_text, re.IGNORECASE)
                    for match in matches:
                        clean_match = re.sub(r'\s+', ' ', match.strip())
                        if clean_match and clean_match not in found_locations:
                            found_locations.append(clean_match)
            
            # Enhanced cell-by-cell search if patterns didn't find specific rooms
            if not any('hall' in loc.lower() or 'room' in loc.lower() for loc in found_locations):
                cells = table.find_all(['td', 'th'])
                
                for cell in cells:
                    text = cell.get_text(strip=True)
                    
                    # Look for room/building references
                    if re.search(r'(?:hall|room|building)\s+\d+', text, re.IGNORECASE):
                        found_locations.append(text)
                    elif re.search(r'frasch\s+\d+', text, re.IGNORECASE):
                        found_locations.append(text)
            
            # If we found specific locations, use them; otherwise search more broadly
            if found_locations:
                locations = found_locations
            else:
                # Fallback to searching cells for location info
                location_keywords = [
                    'room', 'building', 'hall', 'downtown', 'campus', 'center',
                    'internet', 'online', 'web', 'virtual', 'remote', 'distance',
                    'class', 'classroom', 'lab', 'laboratory', 'library',
                    'frasch', 'main', 'north', 'south', 'east', 'west'
                ]
                
                cells = table.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    
                    # Skip enrollment/capacity data that looks like "20 / 22 / 0"
                    if re.match(r'^\d+\s*/\s*\d+\s*/\s*\d+', text):
                        continue
                    
                    # Skip if text contains only numbers, slashes, and "Unlimited"
                    if re.match(r'^[\d\s/]+(?:unlimited|seat|counts|unavailable)*[\s\w]*$', text, re.IGNORECASE):
                        continue
                    
                    if any(keyword in text.lower() for keyword in location_keywords):
                        locations.append(text)
                        break
                
                # If still no locations, look for "Downtown" specifically
                if not locations:
                    if 'downtown' in all_text.lower():
                        locations = ['Downtown']
                    elif 'face-to-face' in all_text.lower() or 'hybrid' in all_text.lower():
                        locations = ['Downtown']  # Default for face-to-face courses
            
            # Final cleanup and fallback
            if not locations:
                locations = [DEFAULT_LOCATION]
            
            print(f"   📍 Extracted locations: {locations}")
            
        except Exception as e:
            print(f"   ⚠️  Location extraction error: {e}")
            locations = [DEFAULT_LOCATION]
        
        return locations

    def extract_instructor_info(self, table):
        """Extract instructor information using reference scraper approach"""
        instructors = [DEFAULT_INSTRUCTOR]
        
        try:
            # Method 1: Use reference scraper approach - look for specific CSS classes
            instructor_cells = table.find_all('td', class_='search-sectioninstructormethods')
            
            found_instructors = []
            for cell in instructor_cells:
                # Extract instructor names using aria-label approach
                instructor_spans = cell.find_all('span', attrs={'aria-label': lambda x: x and 'Faculty Office Hours' in x})
                
                for span in instructor_spans:
                    instructor_name = span.get_text(strip=True)
                    if instructor_name and instructor_name not in found_instructors:
                        found_instructors.append(instructor_name)
                        print(f"   👨‍🏫 Found instructor via CSS: {instructor_name}")
            
            # If found instructors using CSS approach, use them
            if found_instructors:
                instructors = found_instructors
                return instructors
            
            print(f"   ⚠️  No instructors found via CSS approach, trying fallback...")
            
            # Method 2: Fallback - improved version of original approach
            cells = table.find_all(['td', 'th'])
            candidate_instructors = []
            
            for cell in cells:
                text = cell.get_text(strip=True)
                
                # Skip if text is too short or contains excluded keywords
                # Note: Removed 'blended', 'online', 'hybrid' from exclusions to fix the original issue
                if (len(text) < 4 or
                    any(keyword in text.lower() for keyword in [
                        'room', 'time', 'pm', 'am', 'seats', 'enrolled', 'available', 
                        'total', 'waitlist', 'downtown', 'building', 'hall', 'campus',
                        'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
                        'saturday', 'sunday', 'face-to-face',  # Removed 'hybrid', 'online', 'blended'
                        DEFAULT_INSTRUCTOR.lower(), 'course', 'section', 'credit',
                        'start', 'end', 'date', 'week', 'class', 'meeting'
                    ])):
                    continue
                
                # Pattern 1: Look for "Name (Mode)" format
                name_mode_match = re.search(r'^([A-Za-z\s]+)\s*\([^)]*(?:blended|online|hybrid|face-to-face)[^)]*\)', text, re.IGNORECASE)
                if name_mode_match:
                    candidate_name = name_mode_match.group(1).strip()
                    if len(candidate_name) > 3 and any(c.isupper() for c in candidate_name):
                        candidate_instructors.append(candidate_name)
                        print(f"   👨‍🏫 Found instructor via pattern: {candidate_name}")
                        continue
                
                # Pattern 2: Names with space and alphabetic characters
                if (' ' in text and 
                    any(c.isalpha() for c in text) and 
                    not text.replace(' ', '').replace(',', '').replace('.', '').isdigit()):
                    
                    # Additional check: should have at least one capital letter (typical for names)
                    if any(c.isupper() for c in text):
                        candidate_instructors.append(text)
                
                # Pattern 3: Names with comma (Last, First format)
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
                        print(f"   ✅ Selected instructor: {candidate}")
                        break
                else:
                    # Fall back to first candidate if none look ideal
                    instructors = [candidate_instructors[0]]
                    print(f"   ✅ Fallback instructor: {candidate_instructors[0]}")
                    
        except Exception as e:
            print(f"   ❌ Instructor extraction error: {e}")
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