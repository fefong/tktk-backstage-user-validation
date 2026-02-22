# 🚀 Tktk Creator Batch Invitation Bot

Automation script built with Selenium to process TikTok creator
invitations in controlled batches of 30 users.

------------------------------------------------------------------------

## 📖 Overview

This project automates the creator invitation flow inside TikTok Creator
tools, helping streamline large-scale creator outreach safely and
efficiently.

------------------------------------------------------------------------

## ✨ Key Features

-   ✅ Batch processing (30 users per iteration)
-   🔄 Dynamic recalculation of remaining users
-   🧼 React-safe textarea clearing
-   🛑 Manual captcha handling (F8 trigger)
-   🧹 Automatic deduplication of output files
-   🌐 Persistent Chrome session via user profile

------------------------------------------------------------------------

## 🛠 How to Use

### 1️⃣ Install dependencies

``` bash
pip install -r requirements.txt
```

### 2️⃣ Execute the script

``` bash
python script.py
```

### 3️⃣ Start the bot

-   Press **F8**
-   Wait for processing

### 4️⃣ If captcha appears

-   Solve the captcha manually
-   Wait until the validation table loads completely
-   Press **F8** again to continue

The bot will automatically continue processing the next batch until all
users are handled.

------------------------------------------------------------------------

## 📌 Notes

-   Make sure your Chrome profile is properly configured.
-   Do not interrupt the browser while a batch is processing.
-   Output files are automatically cleaned from duplicates at the end of
    execution.
