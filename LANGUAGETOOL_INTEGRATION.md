# LanguageTool API Integration

## Overview

The Discord bot now includes comprehensive grammar and spell checking functionality powered by the LanguageTool API (`https://api.languagetool.org/v2/check`).

## Features

### 🔍 Grammar Checking Commands

#### `/grammar` (Slash Command)
- **Description**: Interactive grammar and spell checking with corrections
- **Usage**: `/grammar text:<your text> language:<optional>`
- **Features**:
  - Interactive button interface
  - Navigate between issues
  - Apply individual corrections
  - Apply all corrections at once
  - Multiple language support

#### `?grammar` (Prefix Command)
- **Description**: Quick grammar check with basic results
- **Usage**: `?grammar <your text>`
- **Features**:
  - Shows up to 3 issues
  - Quick suggestions
  - Links to full interactive checking

#### `?quickfix` 
- **Description**: Automatically applies all grammar fixes
- **Usage**: `?quickfix <your text>`
- **Features**:
  - Instant correction
  - Shows before/after comparison
  - Perfect for quick fixes

#### `?languages`
- **Description**: Shows all supported languages
- **Usage**: `?languages`
- **Features**:
  - Lists all available language codes
  - Usage examples

### 🌍 Supported Languages

- **English**: US, UK, Canada, Australia
- **European**: German, French, Spanish, Italian, Portuguese, Dutch
- **Other**: Russian

### 🎮 Interactive Features

#### Grammar Check View
- **Navigation**: Previous/Next buttons for multiple issues
- **Actions**: Apply fix, Apply all, Ignore
- **Context**: Shows text context around errors
- **Categories**: Spelling, Grammar, Punctuation, Style, etc.

#### Error Types Detected
- **Spelling Errors**: Typos and misspellings
- **Grammar Errors**: Subject-verb agreement, tense errors
- **Punctuation**: Missing commas, periods, etc.
- **Capitalization**: Proper capitalization rules
- **Style**: Writing clarity and flow
- **Word Choice**: Better word suggestions

### 📝 Usage Examples

```bash
# Basic grammar check
?grammar This is a test sentence with some errors.

# Interactive grammar check with language selection
/grammar text:Ceci est un test language:fr

# Quick automatic correction
?quickfix I are going to the store

# View supported languages
?languages
```

### 🛠️ Technical Details

#### API Endpoint
- **URL**: `https://api.languagetool.org/v2/check`
- **Method**: POST
- **Content-Type**: `application/x-www-form-urlencoded`

#### Request Parameters
- `text`: The text to check
- `language`: Language code (e.g., 'en-US')
- `enabledOnly`: Whether to use only enabled rules

#### Response Format
```json
{
  "matches": [
    {
      "message": "Error description",
      "offset": 10,
      "length": 5,
      "replacements": [
        {"value": "suggested replacement"}
      ],
      "rule": {
        "category": {"name": "GRAMMAR"},
        "id": "rule_id"
      }
    }
  ]
}
```

### 🔧 Implementation Files

#### Core Files
- `bot/cogs/grammar_checker.py`: Main grammar checking cog
- `bot/cogs/utils.py`: Quick grammar check integration
- `bot/main_deployment.py`: Cog loading configuration

#### Key Classes
- `GrammarCheckerCog`: Main cog with slash and prefix commands
- `GrammarView`: Interactive Discord UI for corrections
- `HelpCategory`: Updated help system integration

### 📊 Limits and Constraints

- **Text Length**: 2000 characters for full check, 1000 for quick check
- **API Timeout**: 15 seconds for full check, 10 seconds for quick check
- **Rate Limiting**: Managed by LanguageTool API
- **Suggestions**: Limited to 5 per issue for readability

### 🎯 Error Handling

- **Timeout Handling**: Graceful timeout with user feedback
- **API Errors**: Clear error messages with status codes
- **Network Issues**: Retry mechanisms and fallback messages
- **Invalid Text**: Input validation and size limits

### 🚀 Future Enhancements

- **Custom Dictionaries**: Personal word lists
- **Learning Mode**: Track common errors for users
- **Batch Processing**: Multiple text checking
- **Advanced Rules**: Custom grammar rule sets
- **Statistics**: User writing improvement tracking

## Installation Requirements

The LanguageTool integration requires:
- `aiohttp>=3.8.0` (already in requirements)
- `discord.py>=2.3.0` (already in requirements)

No additional API keys or authentication required for the public LanguageTool API.
