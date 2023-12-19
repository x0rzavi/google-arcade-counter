#!/usr/bin/env python

import requests
import re
from bs4 import BeautifulSoup, SoupStrainer
from PIL import Image
import pytesseract

novBadgesList = (
    "Introduction to Large Language Models",
    "Introduction to Generative AI",
    "Introduction to Responsible AI",
    "Digital Transformation with Google Cloud",
    "Innovating with Data and Google Cloud",
    "Infrastructure and Application Modernization with Google Cloud",
    "Understanding Google Cloud Security and Operations",
)

featBadgesList = (
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
)


def getBadges(url: str) -> dict:
    # function to output dictionary of badge name and completion dates
    badgesDict = dict()
    if "://" not in url:
        url = "https://" + url
    html = requests.get(url)
    reqdTags = {
        "div": {"class_": "profile-badges"},
        "ql-dialog": "",
        "title": "",
    }
    reqdContent = SoupStrainer(reqdTags)
    soupContent = BeautifulSoup(html.text, "lxml", parse_only=reqdContent)

    badges = soupContent.find_all("div", class_="profile-badge")
    for badge in badges:
        badgeNameRaw = badge.find("span", class_="l-mts")
        badgeDateRaw = badge.find("span", class_="l-mbs")
        badgeImage = badge.find("img")["src"]
        badgeName = badgeNameRaw.text.strip()
        badgeDate = badgeDateRaw.text.replace("Earned ", "").strip()
        reqdDetails = soupContent.find(
            "ql-dialog", attrs={"headline": badgeName.replace("&", "&amp;")}
        )
        badgeDescRaw = reqdDetails.find("p")
        badgeDesc = badgeDescRaw.text.strip()
        badgesDict[badgeName] = (badgeDate, badgeImage, badgeDesc)

    return badgesDict


def countBadges(badgesDict: dict) -> None:
    # function to print countBadges of badges under appropriate categories
    arcadeLevel = arcadeTrivia = featBadges = normalBadges = novBadges = 0
    patternLevel = r"Level \d+"

    for badge, details in badgesDict.items():
        date = details[0]
        img = details[1]
        desc = details[2]
        if re.search(patternLevel, badge):
            arcadeLevel += 1
        elif "Trivia" in badge:
            arcadeTrivia += 1
        elif badge in novBadgesList:
            novBadges += 1
        elif (badge in featBadgesList) and ("Aug" in date):
            featBadges += 1
        else:
            if "skill badge" in desc:
                normalBadges += 1
            else:
                # detemine if badge is completion badge using OCR
                response = requests.get(img, stream=True)
                image = Image.open(response.raw)
                text = pytesseract.image_to_string(image)
                if "completion" not in text.lower():
                    normalBadges += 1

    total_badges = normalBadges + featBadges
    if (arcadeLevel >= 4) and (arcadeTrivia >= 2) and (total_badges >= 30):
        milestone = "Ultimate Milestone Reached"
        bonusPt = 9
    elif (arcadeLevel >= 4) and (arcadeTrivia >= 2) and (total_badges >= 21):
        milestone = "Milestone 3 Reached"
        bonusPt = 6
    elif (arcadeLevel >= 2) and (arcadeLevel >= 1) and (total_badges >= 15):
        milestone = "Milestone 2 Reached"
        bonusPt = 4
    elif (arcadeLevel >= 2) and (arcadeTrivia >= 1) and (total_badges >= 9):
        milestone = "Milestone 1 Reached"
        bonusPt = 2
    else:
        milestone = "No Milestones Reached"
        bonusPt = 0

    normalBadgesPt = normalBadges // 3
    featBadgesPt = 2 * (featBadges // 3)
    normalBadgesRem = 3 - normalBadges % 3
    featBadgesRem = 3 - featBadges % 3
    totalBadgesRem = normalBadgesRem + featBadgesRem
    totalBadgesRemPt = totalBadgesRem // 3
    total_pt = (
        arcadeLevel
        + arcadeTrivia
        + normalBadgesPt
        + featBadgesPt
        + novBadges
        + bonusPt
        + totalBadgesRemPt
    )

    print()
    print("Arcade Level Badges: {} | Points: {}".format(arcadeLevel, arcadeLevel))
    print("Arcade Trivia Badges: {} | Points: {}".format(arcadeTrivia, arcadeTrivia))
    print("Skill Badges: {} | Points: {}".format(normalBadges, normalBadgesPt))
    print("Featured Skill Badges: {} | Points: {}".format(featBadges, featBadgesPt))
    print("November Badges: {} | Points: {}".format(novBadges, novBadges))
    print("Total Arcade Points: {}".format(total_pt))
    print(milestone)
    print()

    if normalBadges % 3 != 0:
        print(
            "Complete {} More Skill Badges to +1 Arcade Point!".format(normalBadgesRem)
        )
    # November is already over :)
    # if featBadges % 3 != 0:
    #     print(
    #         "Complete {} More Featured Skill Badges to +1 Arcade Point!".format(
    #             featBadgesRem
    #         )
    #     )


while True:
    url = input("Enter Google Skills Boost Profile URL: ")
    countBadges(getBadges(url))
    print()
