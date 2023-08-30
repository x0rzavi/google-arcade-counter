#!/usr/bin/env python

import requests
import re
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract

feat_badges_list = [
    "Create and Manage Cloud Resources",
    "Perform Foundational Infrastructure Tasks in Google Cloud",
    "Perform Foundational Data, ML, and AI Tasks in Google Cloud",
    "Configure Service Accounts and IAM Roles for Google Cloud",
    "Integrate BigQuery Data and Google Workspace using Apps Script",
    "Develop with Apps Script and AppSheet",
    "Set Up and Configure a Cloud Environment in Google Cloud",
    "Create ML Models with BigQuery ML",
    "Exploring Data with Looker",
    "Secure BigLake Data",
    "Protect Sensitive Data with Data Loss Prevention",
    "Tag and Discover BigLake Data",
    "Store, Process, and Manage Data on Google Cloud - Console",
    "Analyze BigQuery Data in Connected Sheets",
    "Optimize Costs for Google Kubernetes Engine",
    "Get Started with Eventarc",
    "Get Started with Dataplex",
    "Get Started with Pub/Sub",
    "Automating Infrastructure on Google Cloud with Terraform",
    "Deploy and Manage Cloud Environments with Google Cloud",
    "Ensure Access & Identity in Google Cloud",
    "Create a Streaming Data Lake on Cloud Storage",
    "Use APIs to Work with Cloud Storage",
    "App Engine: 3 Ways",
    "Serverless Firebase Development",
    "Cloud Architecture: Design, Implement, and Manage",
    "Engineer Data in Google Cloud",
    "The Basics of Google Cloud Compute",
    "Networking Fundamentals on Google Cloud",
    "Streaming Analytics into BigQuery",
]

def badges(url):
    # function to output dictionary of badge name and completion dates
    # only SKILL badges and NOT COMPLETION badges
    global soup, name
    if "://" in url:
        pass
    else:
        url = "https://" + url
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')

    try:
        badges_dict = dict()
        badges = soup.find_all('div', class_='profile-badge')
        name = soup.find('h1', class_='ql-headline-1').text
        for badge in badges:
            badge_name_raw = badge.find('span', class_='ql-subhead-1 l-mts')
            badge_date_raw = badge.find('span', class_='ql-body-2 l-mbs')
            badge_name = badge_name_raw.text.strip()
            badge_date = badge_date_raw.text.replace('Earned ', '').strip()
            badges_dict[badge_name] = badge_date

        return badges_dict
    except Exception:
        pass

def count(badges_dict):
    # function to print count of badges under appropriate categories
    arcade_level = arcade_trivia = feat_badges = normal_badges = 0
    pattern_level = r'Level \d+'

    for badge in badges_dict:
        if re.search(pattern_level, badge):
            arcade_level += 1
        elif 'Trivia' in badge:
            arcade_trivia += 1
        elif (badge in feat_badges_list) and ('Aug' in badges_dict[badge]):
            feat_badges += 1
        else:
            try:
                dialog = soup.find('ql-dialog', {'headline': badge})
                badge_desc = dialog.find('p').text
            except Exception:
                pass

            if 'skill badge' in badge_desc:
                normal_badges += 1
            else:
                # detemine if badge is completion badge using OCR
                try:
                    img = soup.find('img', {'alt': 'Badge for ' + badge})
                    src = img['src']
                    response = requests.get(src, stream=True)
                    image = Image.open(response.raw)
                    text = pytesseract.image_to_string(image)
                except Exception:
                    pass
                if 'completion' not in text.lower():
                    normal_badges += 1

    total_badges = normal_badges + feat_badges
    if (arcade_level >= 4) and (arcade_trivia >= 2) and (total_badges >= 30):
        milestone = 'Ultimate Milestone Reached'
        bonus_pt = 10
    elif (arcade_level >= 4) and (arcade_trivia >= 2) and (total_badges >= 21):
        milestone = 'Milestone 3 Reached'
        bonus_pt = 6
    elif (arcade_level >= 2) and (arcade_level >= 1) and (total_badges >= 15):
        milestone = 'Milestone 2 Reached'
        bonus_pt = 4
    elif (arcade_level >= 2) and (arcade_trivia >= 1) and (total_badges >= 9):
        milestone = 'Milestone 1 Reached'
        bonus_pt = 2
    else:
        milestone = 'No Milestones Reached'
        bonus_pt = 0

    normal_badges_pt = normal_badges // 3
    feat_badges_pt = 2 * (feat_badges // 3)
    normal_badges_rem = 3 - normal_badges % 3
    feat_badges_rem = 3 - feat_badges % 3
    total_badges_rem = normal_badges_rem + feat_badges_rem 
    total_badges_rem_pt = total_badges_rem // 3
    total_pt = arcade_level + arcade_trivia + normal_badges_pt + feat_badges_pt \
        + bonus_pt + total_badges_rem_pt

    print()
    print('Greetings!', name)
    print('Arcade Level Badges: {} | Points: {}'.format(arcade_level, arcade_level))
    print('Arcade Trivia Badges: {} | Points: {}'.format(arcade_trivia, arcade_trivia))
    print('Skill Badges: {} | Points: {}'.format(normal_badges, normal_badges_pt))
    print('Featured Skill Badges: {} | Points: {}'.format(feat_badges, feat_badges_pt))
    print('Total Arcade Points: {}'.format(total_pt))
    print(milestone)
    print()

    if (normal_badges % 3 != 0):
        print('Complete {} More Skill Badges to +1 Arcade Point!'\
              .format(normal_badges_rem))
    if (feat_badges % 3 != 0):
        print('Complete {} More Featured Skill Badges to +1 Arcade Point!'\
              .format(feat_badges_rem))

while (True):
    url = str(input('Enter Google Skills Boost Profile URL: '))
    count(badges(url))
    print()
