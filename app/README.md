# SourceWell Project - App Module

## Overview

The `app` module is the main web interface for the SourceWell Healthcare Platform, built with Streamlit to provide an interactive healthcare risk assessment application. This module serves as the primary user interface for collecting patient data, running evidence-based risk calculations, and presenting results with AI-powered insights.

## Architecture

### Main Components

```
app/
├── main.py                     # Application entry point
├── __init__.py                 # Package initialization
├── ui/
│   ├── __init__.py            # UI package initialization
│   ├── main_interface.py       # Main interface orchestration
│   ├── styles/
│   │   └── custom.css         # Custom styling
│   ├── pages/                 # Individual page modules
│   │   ├── __init__.py        # Pages package initialization
│   │   ├── assessment.py      # Risk calculator execution
│   │   ├── coaching.py        # Health guidance
│   │   ├── history.py         # Patient data collection
│   │   └── report.py          # Explanations and recommendations
│   └── components/            # Reusable UI components
│       ├── citation_viewer.py # Medical citation display
│       ├── patient_forms.py   # Patient data collection forms
│       ├── results_display.py # Results presentation
│       └── risk_dashboard.py  # Risk assessment visualization
```

### Core Classes

#### SourceWellInterface

The main orchestration class that manages:

- Session state for patient data, risk results, and AI explanations
- Navigation between application pages
- Component initialization and coordination
- Custom CSS styling integration

#### RiskDashboard

Comprehensive risk assessment system featuring:

- Integration with MultiCalculatorRunner for risk calculations
- Visual risk summaries with interactive cards and metrics
- Plotly-based charts (bar charts, gauge charts)
- Risk factors analysis with priority actions
- Error handling for calculator failures

## Features

### Multi-Page Navigation

- **Patient History**: Patient data collection and management
- **Assessment**: Risk calculator execution (FINDRISC diabetes, Framingham cardiovascular, colorectal screening)
- **Report**: AI-powered explanations and recommendations
- **Coaching**: Personalized health guidance

### Risk Assessment Capabilities

- **FINDRISC Calculator**: 10-year Type 2 Diabetes risk assessment
- **Framingham Calculator**: Cardiovascular disease risk calculation
- **Colorectal Screening**: Cancer screening recommendations
- **Visual Analytics**: Interactive charts and progress indicators
- **Risk Stratification**: Color-coded risk levels and priority actions

### User Interface Features

- Responsive design with custom CSS styling
- Progress indicators for multi-step workflows
- Session state persistence
- Error handling and user feedback
- Debug information toggle for development

## Technical Implementation

### Framework & Libraries

- **Streamlit**: Web application framework
- **Plotly**: Interactive data visualization (charts, gauges)
- **Python Path Management**: Dynamic module imports

### Configuration Management

- Uses `sourcewell_config.json` for environment configuration
- Sets cache paths for Hugging Face, temporary files, and pip cache
- Environment variable management

### Data Flow

1. Patient data collection through PatientDataCollector
2. Risk calculation via MultiCalculatorRunner integration
3. Results visualization through RiskDashboard
4. AI-powered insights and recommendations

### Session Management

The application maintains persistent session state for:

- `patient_data`: Collected patient information
- `risk_results`: Calculator outputs and assessments
- `ai_explanations`: Generated insights and recommendations
- `form_data`: Form input persistence
- `ai_engine`: AI processing engine state

## Module Dependencies

### Internal Dependencies

- `/calculators`: Risk assessment calculations (MultiCalculatorRunner)
- `/knowledge_base`: Medical search engine integration
- `/data_models`: Patient data structures (PatientData)

### External Dependencies

- `streamlit`: Web application framework
- `plotly`: Data visualization library (plotly.graph_objects, plotly.express)
- `pathlib`: File path management
- `json`: Configuration file parsing
- `os`: Environment variable management
- `sys`: Python path manipulation

## Usage

### Running the Application

```bash
# From project root
streamlit run app/main.py
```

### Configuration

The application reads configuration from `sourcewell_config.json` in the project root for:

- Cache directory paths
- Environment variable setup
- System configuration

### Page Flow

1. **Patient History**: Collect and validate patient data
2. **Assessment**: Select and run risk calculators
3. **Report**: View AI-generated explanations and recommendations
4. **Coaching**: Access personalized health guidance

## Risk Visualization Features

### Risk Visualization

- **Risk Cards**: Individual calculator results with color coding
- **Comparison Charts**: Side-by-side risk assessment visualization
- **Gauge Charts**: Risk level indicators with thresholds
- **Progress Bars**: Score visualization for assessment tools

### Risk Analysis

- **Priority Actions**: Critical recommendations highlighted
- **Risk Factors**: Identified risk factors from assessments
- **Risk Categorization**: Risk level categorization and color coding
- **Success Indicators**: Low-risk confirmations

## Error Handling

The application includes comprehensive error handling for:

- Missing patient data validation
- Calculator execution failures
- Session state management issues
- File loading and configuration errors

## Development Features

- Debug information toggle for development
- Session state inspection
- Component state monitoring
- Configuration validation

This module serves as the primary interface for users to access evidence-based risk assessments through an intuitive, interactive web application.
