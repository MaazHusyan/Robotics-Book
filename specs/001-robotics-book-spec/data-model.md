# Data Model

**Feature**: Physical and Humanoid Robotics Book  
**Date**: 2025-12-07  
**Phase**: 1 - Design & Contracts

## Content Entities

### Chapter
**Purpose**: Represents a major book chapter with multiple modules  
**Attributes**:
- chapter_number: Integer (1-7)
- title: String (chapter title)
- description: String (chapter overview)
- learning_objectives: Array[String] (3-5 objectives per chapter)
- prerequisites: Array[String] (required background knowledge)
- modules: Array[Module] (child modules)

**Validation Rules**:
- chapter_number must be unique and sequential (1-7)
- title must be descriptive and follow naming convention
- learning_objectives required for each chapter
- modules must be ordered logically

### Module
**Purpose**: Individual learning module within a chapter  
**Attributes**:
- module_number: String (e.g., "01", "02")
- title: String (module title)
- content_type: Enum ["theory", "practical", "case_study", "hands_on"]
- estimated_reading_time: Integer (minutes)
- difficulty_level: Enum ["beginner", "intermediate", "advanced"]
- code_examples: Array[CodeExample]
- references: Array[Reference]
- exercises: Array[Exercise]

**Validation Rules**:
- module_number must be unique within chapter
- title must be descriptive and follow kebab-case for URLs
- content_type determines required content structure
- difficulty_level must align with chapter progression

### CodeExample
**Purpose**: Executable code examples for practical learning  
**Attributes**:
- language: Enum ["python", "cpp", "javascript", "ros2"]
- title: String (descriptive title)
- description: String (what code demonstrates)
- code: String (executable code)
- explanation: String (step-by-step explanation)
- dependencies: Array[String] (required libraries/packages)
- testing_notes: String (how to verify code works)

**Validation Rules**:
- language must match module context
- code must be syntactically correct and tested
- dependencies must be specified with versions
- explanation must be clear for target audience

### Reference
**Purpose**: Academic and industry citations  
**Attributes**:
- type: Enum ["ieee", "academic_paper", "documentation", "website", "book"]
- title: String (reference title)
- authors: Array[String] (author names)
- publication_year: Integer (year of publication)
- url: String (link to source)
- doi: String (digital object identifier, if applicable)
- relevance: String (why this reference is included)

**Validation Rules**:
- url must be accessible and current
- publication_year must be within acceptable range (historical exceptions allowed)
- academic papers must be peer-reviewed
- documentation must be from official sources

### Exercise
**Purpose**: Hands-on learning activities  
**Attributes**:
- type: Enum ["theory_question", "coding_challenge", "simulation", "research"]
- title: String (exercise title)
- description: String (detailed instructions)
- difficulty: Enum ["easy", "medium", "hard"]
- estimated_time: Integer (minutes to complete)
- solution_hints: Array[String] (progressive hints)
- expected_outcome: String (what student should achieve)

**Validation Rules**:
- difficulty must align with module difficulty_level
- estimated_time must be realistic
- solution_hints must provide progressive assistance
- expected_outcome must be measurable

## Configuration Entities

### DocusaurusConfig
**Purpose**: Site configuration and theme settings  
**Attributes**:
- site_title: String ("Physical and Humanoid Robotics")
- tagline: String ("From Fundamentals to Advanced Applications")
- url: String (GitHub Pages URL)
- base_url: String (path prefix)
- primary_color: String ("#0066cc")
- accent_color: String ("#00d4ff")
- default_theme: String ("dark")
- navbar_items: Array[NavbarItem]
- footer_config: FooterConfig

**Validation Rules**:
- Colors must be valid hex codes
- URL must be valid and accessible
- Theme configuration must support accessibility

### NavbarItem
**Purpose**: Navigation menu items  
**Attributes**:
- label: String (display text)
- to: String (internal path)
- type: Enum ["doc", "page", "link", "dropdown"]
- position: Integer (order in navbar)
- active_regex: String (when item is highlighted)

**Validation Rules**:
- to must be valid path for site structure
- position must create logical navigation flow
- active_regex must match appropriate pages

### SidebarCategory
**Purpose**: Chapter organization in sidebar  
**Attributes**:
- type: String ("category")
- label: String (chapter title)
- collapsible: Boolean (true)
- collapsed: Boolean (false for top-level)
- items: Array[SidebarItem]

**Validation Rules**:
- label must match chapter title exactly
- items must include all chapter modules
- nesting must not exceed 2 levels

## Content Relationships

### Chapter-Module Relationship
- One Chapter has many Modules (1:N)
- Modules belong to exactly one Chapter
- Module ordering within Chapter is significant

### Module-CodeExample Relationship
- One Module has many CodeExamples (1:N)
- CodeExamples belong to exactly one Module
- CodeExamples are ordered within Module

### Module-Reference Relationship
- One Module has many References (1:N)
- References can be shared across Modules
- References are ordered by relevance

### Module-Exercise Relationship
- One Module has many Exercises (1:N)
- Exercises belong to exactly one Module
- Exercises are ordered by difficulty

## State Transitions

### Content Creation Workflow
1. **Draft** → **Technical Review** → **Editorial Review** → **Ethics Review** → **Approved**
2. **Approved** → **Published** → **Live**
3. **Live** → **Update** → **Review Cycle** → **Published**

### Quality Gates
- **Technical Review**: Accuracy and code verification
- **Editorial Review**: Clarity and accessibility
- **Ethics Review**: Bias and inclusivity assessment
- **Final Approval**: Constitution compliance check

## Data Integrity Constraints

### Uniqueness Constraints
- Chapter numbers must be unique (1-7)
- Module numbers must be unique within chapter
- Reference URLs must be unique across site
- Code example titles must be unique within module

### Referential Integrity
- All modules must reference valid chapter
- All code examples must reference valid module
- All references must have accessible URLs
- All exercises must reference valid module

### Data Quality Rules
- All content must pass constitution compliance checks
- Code examples must be tested and verified
- References must be current and authoritative
- Exercises must have measurable outcomes

## Performance Considerations

### Content Loading
- Module content should be <100KB for fast loading
- Code examples should be <10KB each
- Images should be optimized and compressed
- Total chapter size should be <500KB

### Search Optimization
- All content must have searchable titles and descriptions
- Code examples should include searchable comments
- References should be indexed by author and title
- Exercises should be searchable by topic and difficulty

## Security and Privacy

### Content Security
- All code examples must be security-reviewed
- External links must use HTTPS where available
- User data collection must be disclosed
- No tracking scripts without consent

### Intellectual Property
- All content must be original or properly attributed
- Code examples must use permissive licenses
- Images must have appropriate licenses
- References must follow citation standards