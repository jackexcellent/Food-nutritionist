# Food-nutritionist 食物營養師 Discord 機器人

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Discord](https://img.shields.io/badge/discord.py-2.x-blueviolet)

## 專案簡介 Project Introduction

本專案是一個 Discord 機器人，結合食物圖像辨識（nateraw/food）、營養成分查詢、及大語言模型（LLM，支援繁體中文/台灣飲食文化），自動協助使用者分析餐點、推薦健康飲食建議，適合推廣健康生活與體重管理。

This project is a Discord bot that uses image recognition (nateraw/food), nutrition lookup, and LLM for personalized food analysis and dietary suggestions. It supports Traditional Chinese and Taiwan food culture.

---

## 主要功能 Features

- **圖片辨識**：上傳食物照片自動辨識內容
- **營養查詢**：回傳食物熱量、碳水、蛋白質、脂肪等資訊
- **AI 飲食建議**：依健康（healthy）或減重（weight_loss）目標，產生個人化建議
- **自然語言問答**：可直接在 Discord 詢問與飲食/營養相關問題
- **快取機制**：減少重複查詢與 API 次數

---

## 檔案結構 File Structure

```
food_nutritionist/
├── bot.py                 # 啟動點，僅做 Discord bot 啟動
├── config.py              # 管理設定與環境變數
├── core/
│   ├── __init__.py
│   ├── discord_handler.py # 指令與回應邏輯
│   ├── image_recognition.py
│   ├── nutrition.py       # 營養查詢/快取
│   ├── llm.py             # LLM 相關
│   └── utils.py
├── cache/
│   ├── nutrition_cache.json
│   └── recommendation_cache.json
├── img/                   # 如果有任何圖片放在這
│   └──
├── tests/                 # 如果有任何測試檔放在這
│   ├──
│   └── ...
├── requirements.txt
├── .env
└── README.md
```

---

## 安裝與執行 Installation & Run

### 1. 環境需求 Requirements

- Python 3.8+
- [discord.py](https://discordpy.readthedocs.io/)
- torch、transformers、Pillow、requests、python-dotenv

### 2. 安裝套件 Install dependencies

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數 Configure Environment Variables

建立 `.env` 或 `test.env` 檔案於專案根目錄，內容格式如下：

```
DISCORD_BOT_API_KEY=你的 Discord Bot Token
GEMINI_API_KEY=你的 gemini API 金鑰
# 其他必要金鑰...
```

### 4. 執行機器人 Run the bot

```bash
python bot.py
```

---

## 使用方式 Usage

### Discord 指令

- `!hello`  
  機器人打招呼

- `!analyze [healthy|weight_loss]`  
  上傳食物圖片，選擇分析目標（預設 healthy），機器人回傳辨識結果、營養數據與飲食建議

- `!ask [問題內容]`  
  直接詢問營養、健康、熱量等問題，AI 回答（支援繁體中文）

---

## 重要說明 Notes

- 圖像辨識使用 [nateraw/food](https://huggingface.co/nateraw/food) 預訓練模型
- 須自備 Discord Bot Token、Gemini API 金鑰
- 若有 API 限額建議使用快取檔案
- 支援台灣常見飲食文化與本地化建議

## Contribution guidelines

### Commit message guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for commit messages.

- Each commit message should start with a type, followed by a scope (optional), and then a description. For example:
  - `feat(core): add new authentication module`
  - `fix(api): resolve issue with user login`
  - `docs(readme): update installation instructions`
- The entire commit message should be structured as follows:

  ```
  <type>(<scope>): <description>

  [optional body]

  [optional footer]
  ```

- The type should be one of the following:

  | Type     | Description                                                                        | Example                                                       |
  | -------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------- |
  | fix      | A bug fix in the project                                                           | `fix(docs): correct broken hyperlink in documentation`        |
  | feat     | New feature(s) being added to the project                                          | `feat(calendar): add new calendar feature`                    |
  | docs     | A new addition or update to the docs site and/or documentation                     | `docs(readme): add installation instructions`                 |
  | test     | New tests being added to the project                                               | `test(mobile): add Playwright tests for mobile docs site`     |
  | chore    | Tasks that don't modify any business logic code and that help maintain the project | `chore(deps): update project dependencies`                    |
  | style    | Changes that do not affect the meaning of the code and that improve readability    | `style(core): reformat code for readability`                  |
  | refactor | A change that improves the readability of code itself without modifying behavior   | `refactor(auth): extract helper function for validation`      |
  | perf     | A code change that improves code performance                                       | `perf(api): optimize data fetching logic`                     |
  | build    | Changes that affect the build system or external dependencies                      | `build(deps): upgrade to latest webpack version`              |
  | ci       | Changes to our CI configuration files and scripts                                  | `ci(github): add new workflow for automated testing`          |
  | revert   | Reverting a previous commit                                                        | `revert(core): revert commit abc123 that caused a regression` |

- Each commit should be a single logical change. Don't make several logical changes in one commit. For example, if a patch fixes a bug and optimizes the performance of a feature, split it into two separate commits.

- Each commit should be able to stand on its own, and each commit should build on the previous one. This way, if a commit introduces a bug, it should be easy to identify and revert.

- Each commit should be deployable and not break the build, tests, or functionality.

- If you ever amend, reorder, or rebase, your local branch will become divergent from the remote for the amended commit(s), so GitHub won't let you push. Simply force push to overwrite your old branch: `git push --force-with-lease`.
