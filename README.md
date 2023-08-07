# JPoetry
![telegram-cloud-photo-size-2-5370743251327372739-y](https://github.com/Bobronium/jpoetry/assets/36469655/7f9708e3-e632-472a-af65-08be89d4b9c1)

---

## 👨‍💻Author's note
I've developed and deployed this project a while ago, but never shared it to allow contribution and transparency. Now it's time to fix it. 
This README is generated via LLM, so it's not ideal, but I like how it picked up on the essence and deacribed modules. Shoutout to @eli64s for his https://github.com/eli64s/README-AI 🙌

## 💬 Usecase: 
Add bot to the group and passively wait until some message will fit into a poetic figure. JPoetry will pick up on this and will generate an image with related message.

Check it out at https://t.me/JPoetryBot



## 📍 Overview

The jpoetry project is a Telegram bot that converts messages into poetic format using natural language processing techniques. It offers core functionalities such as generating different types of poems from given messages, providing cheat sheets with information on poem types and genres, and creating beautiful images representing the poems. The bot enhances the messaging experience by adding a touch of creativity and cultural enrichment through the art of poetry.

---

## ⚙️ Features

| Feature                | Description                                                                                                                                                                                                                                                 |
| ---------------------- |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **⚙️ Architecture**     | The codebase follows a modular architecture with separate modules for different functionalities. It uses the aiogram library for interacting with the Telegram Bot API. The project also includes Docker images for development and deployment stages.      |
| **🔗 Dependencies**    | The project relies on external libraries such as Poetry and aiogram. These libraries provide additional functionalities and simplify development.                                                                                                           |
| **🧩 Modularity**      | The codebase is well-organized into smaller, modular components, such as `config.py`, `poetry.py`, `answers.py`, and `bot.py`. Each module focuses on a specific aspect of the system's functionality, providing maintainability and ease of understanding. |
| **✔️ Testing**          | The codebase currently does not provide explicit information on testing strategies or tools being used. Implementation of automated tests using frameworks such as pytest would be beneficial for ensuring the stability and correctness of the project.    |
| **⚡️ Performance**      | The codebase does not explicitly mention performance optimization techniques. However, the use of frameworks like aiogram and efficient algorithm design in modules like `poetry.py` indicates considerations for performance.                              |
| **🔐 Security**        | The codebase exhibits few security measures, such as leveraging environment variables for access tokens. Further security measures, such as input validation and sanitization, are essential to prevent malicious attacks and secure sensitive user data.   |
| **🔀 Version Control** | The codebase currently uses Git for version control. It is advisable to follow best practices, such as providing clear commit messages and maintaining a structured branching strategy, to facilitate collaboration and codebase management.                |
| **🔌 Integrations**    | The project integrates with the Telegram Bot API through the aiogram library. The use of image manipulation libraries and TrueType font files indicates potential integration with external image generation services or libraries for creating poetry images. |
| **📶 Scalability**     | The codebase does not specifically address scalability. However, the modular architecture provides a foundation for introducing scalability measures such as load balancing, distributed processing, and caching for handling increased usage and growth.   |

---


## 📂 Project Structure




---

## 🧩 Modules

<details closed><summary>Root</summary>

| File       | Summary                                                                                                                                                                                                                                                                                                                                       |
| ---        |-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Dockerfile | This code module sets up multiple container images for different stages of development and deployment. It installs dependencies using Poetry and creates a virtual environment for building and running the Python application. The "development" image is used for testing, while the "runtime" image is used for deploying the application. |
| Makefile   | This code module provides a set of make targets for the JPoetry project. It includes commands for formatting, testing and linting. It also includes options for cleaning up build artifacts and generating coverage reports.                                                                                                                  |
| README.MD  | jpoetry is a Telegram bot that converts messages into poetic format. It uses natural language processing techniques to analyze messages and generate poetic responses.                                                                                                                                                                        |

</details>

<details closed><summary>jpoetry</summary>

| File         | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---          | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| config.py    | This code module defines various constants and imports necessary libraries. It provides the path to a TrueType font file and extracts known glyphs from the font. It also sets base and accent colors and retrieves a bot token from an environment variable.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| poetry.py    | This code module provides functionality for detecting and generating poems of specific genres. It analyzes text, counts syllables, and checks for poem structure and composition. The module includes functions for iterating and detecting poems, as well as dataclasses to represent poetry phrases and the poems themselves. It also contains error handling for issues such as incorrect syllable count and unsupported characters.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| answers.py   | In this code module, the core functionalities include generating different types of poems from given messages, obtaining cheat sheets with information on poem types and genres, and providing welcome and help text for users.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| templates.py | This code defines configurations for generating poetry images and creates a mapping of genres to corresponding image info. It also sets specific text configurations for the author and phrases. Additionally, there is a dictionary mapping the number of syllables in a phrase to its corresponding phrases configuration.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| bot.py       | This code module is responsible for handling commands, messages, and inline queries for a poetry bot. It utilizes the aiogram library for interacting with the Telegram Bot API. The code module includes the following key functionalities:1. Logging configuration: InterceptHandler is created to handle logging events, and loguru library is used for logging configuration.2. Bot and Dispatcher initialization: The bot is initialized with a bot token and parse mode for markdown. The dispatcher is initialized with the bot.3. Command handlers: There are command handlers for the "/start", "/help", "/info", and "/stats" commands. These handlers reply to the user with appropriate messages or statistics.4. Message handler: There is a message handler that detects and sends poems in response to text messages. It checks if a message is from a person or a group and tracks the number of messages handled for the last 24 hours.5. Inline query handler: There is an inline query handler that detects and sends poems in response to inline queries. It also tracks the number of inline requests for the last 24 hours.6. Poetry generation and image creation: The code module includes functions for generating poems and creating images representing the poems. The "detect_and_send_poem" function is responsible for detecting poems in a message and sending the corresponding images with the detected poems.These functionalities work together to provide a poetry bot that can generate and display poems in response to commands, messages, and inline queries. |
| utils.py     | The provided code module includes a `DataModel` class inherited from `BaseModel`, representing a data model with arbitrary types. It also contains a `Timer` class for measuring elapsed time and a `TimeAwareCounter` class for counting occurrences within a specific time period. The code module implements functionalities such as timing code execution and counting occurrences with timestamps.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| text.py      | This code module provides various functions for working with text in Cyrillic and Latin languages. It includes functionality for removing unsupported characters, parsing words, converting quantitative numbers to numerals, spelling out numbers in Cyrillic, counting syllables in words, extracting information about words in a line of text, and agreement of words with numbers. These functions are designed to handle different scenarios with input validation and error handling.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| image.py     | The provided code module allows for adding text to an image based on a predefined template. It supports customizing text size, position, color, and anchor point. The module also handles font scaling to fit the text within specified boundaries. It can then generate and return the modified image as a byte stream.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| __main__.py  | This code module executes the jpoetry bot, utilizing the aiogram library's executor function to start polling for updates and skip any existing updates.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| textpy.py    | This code module defines the core functionalities of handling and manipulating word and syllable information, including data structures and error handling. It provides classes for representing word information, line information, and specific types of errors. It also includes a translation mapping for converting numbers to superscript symbols.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

</details>

---

## 🚀 Getting Started

### ✔️ Prerequisites

Before you begin, ensure that you have the following prerequisites installed:
> - `ℹ️ Requirement 1`
> - `ℹ️ Requirement 2`
> - `ℹ️ ...`

### 📦 Installation

1. Clone the  repository:
```sh
git clone https://github.com/Bobronium/jpoetry
```

2. Change to the project directory:
```sh
cd jpoetry
```

3. Install the dependencies:
```sh
python -m venv .venv && .venv/bin/pip install . 
```

### 🎮 Using 

## Docker
1. Build container
```sh
docker build -t jpoetry .
```
2. Run
```sh
docker run -e BOT_TOKEN=<your-telegram-bot-token> jpoetry 
```
## Locally
```sh
python -m jpoetry
```

### 🧪 Running Tests
```sh
make test
```

---

## 🤝 Contributing


---

Contributions are always welcome! Please follow these steps:
1. Fork the project repository. This creates a copy of the project on your account that you can modify without affecting the original project.
2. Clone the forked repository to your local machine using a Git client like Git or GitHub Desktop.
3. Create a new branch with a descriptive name (e.g., `new-feature-branch` or `bugfix-issue-123`).
```sh
git checkout -b new-feature-branch
```
4. Make changes to the project's codebase.
5. Commit your changes to your local branch with a clear commit message that explains the changes you've made.
```sh
git commit -m 'Implemented new feature.'
```
6. Push your changes to your forked repository on GitHub using the following command
```sh
git push origin new-feature-branch
```
7. Create a new pull request to the original project repository. In the pull request, describe the changes you've made and why they're necessary.
The project maintainers will review your changes and provide feedback or merge them into the main branch.

---

## 📄 License

This project is licensed under the `Mozilla Public License v 2.0` License. See the [LICENSE](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-license-to-a-repository) file for additional info.

## 👏 Acknowledgments

> This readme was partially generated via https://github.com/eli64s/README-AI
> Special thanks to Sasha Antropova for helping out with image templates, you can check her Behance [here](https://www.behance.net/antrpva1e87).

---
