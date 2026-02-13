"""
Configuration file for Unit Extraction Tool
"""

# Logical repository list (user-facing)
REPOS = ['ssa', 'mena', 'cist', 'ldn', 'weu', 'isr', 'pol', 'cee']

# Repository variants/suffixes
REPO_VARIANTS = ['db', 'fe']

# Branch mapping
BRANCH_MAPPING = {
    'CIT': 'release/develop',
    'BFX': 'release/release',
    'PROD': 'main'
}

# Clone URLs for each repository variant
# Format: {logical_repo: {variant: clone_url}}
CLONE_URLS = {
    'ssa': {
        'db': 'git@github.com:yourorg/ssa-db.git',
        'fe': 'git@github.com:yourorg/ssa-fe.git'
    },
    'mena': {
        'db': 'git@github.com:yourorg/mena-db.git',
        'fe': 'git@github.com:yourorg/mena-fe.git'
    },
    'cist': {
        'db': 'git@github.com:yourorg/cist-db.git',
        'fe': 'git@github.com:yourorg/cist-fe.git'
    },
    'ldn': {
        'db': 'git@github.com:yourorg/ldn-db.git',
        'fe': 'git@github.com:yourorg/ldn-fe.git'
    },
    'weu': {
        'db': 'git@github.com:yourorg/weu-db.git',
        'fe': 'git@github.com:yourorg/weu-fe.git'
    },
    'isr': {
        'db': 'git@github.com:yourorg/isr-db.git',
        'fe': 'git@github.com:yourorg/isr-fe.git'
    },
    'pol': {
        'db': 'git@github.com:yourorg/pol-db.git',
        'fe': 'git@github.com:yourorg/pol-fe.git'
    },
    'cee': {
        'db': 'git@github.com:yourorg/cee-db.git',
        'fe': 'git@github.com:yourorg/cee-fe.git'
    }
}

# File extension specific to FE variant
FE_FILE_EXTENSION = '.fmb'

# Jira pattern - matches BANKING-123456 with or without brackets
JIRA_REGEX_PATTERN = r'[A-Z]+-\d+'

# Git log format
GIT_LOG_FORMAT = '%H|%s'

# File status indicators in git log
FILE_STATUS = {
    'A': 'Added',
    'M': 'Modified',
    'D': 'Deleted',
    'R': 'Renamed',
    'C': 'Copied'
}