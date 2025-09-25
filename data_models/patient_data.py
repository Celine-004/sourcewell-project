"""
Patient Data Model

Pure patient data management with validation and normalization.
BMI automatically calculated from height and weight with clinical categorization.
"""

from dataclasses import dataclass, field, fields
from typing import Dict, Any, List, Optional, ClassVar
from datetime import datetime

@dataclass
class PatientData:   

    age: int
    gender: str
    
    height_cm: float
    weight_kg: float
    waist_circumference: Optional[int] = None
    
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    total_cholesterol: Optional[int] = None
    hdl_cholesterol: Optional[int] = None
    
    family_diabetes_history: str = 'none'  # 'none', 'grandparent_aunt_uncle_cousin', 'parent_sibling_child'
    high_glucose_history: bool = False
    diabetes_diagnosed: bool = False
    
    # Medical History - Cardiovascular
    hypertension_medication: bool = False
    current_smoker: bool = False
    
    # Medical History - Cancer Screening
    family_colorectal_cancer: bool = False
    family_colorectal_age: Optional[int] = None
    personal_history_polyps: bool = False
    inflammatory_bowel_disease: bool = False
    high_risk_syndrome: bool = False
    # Screening History
    previous_screening_date: Optional[str] = None  # 'YYYY-MM-DD'
    previous_screening_method: Optional[str] = None  # 'colonoscopy', 'fit', 'cologuard'
    
    physical_activity: bool = True
    vegetable_fruit_daily: bool = True
    
    created_date: str = field(default_factory=lambda: datetime.now().isoformat()[:19])
    
    # Computed properties (not user input)
    bmi: Optional[float] = field(init=False, default=None)
    bmi_category: Optional[str] = field(init=False, default=None)
    
    # WHO BMI Categories for clinical interpretation
    BMI_CATEGORIES: ClassVar[List[tuple]] = [
        (0.0, 16.0, "Severe Underweight"),
        (16.0, 18.5, "Underweight"), 
        (18.5, 25.0, "Normal Weight"),
        (25.0, 30.0, "Overweight"),
        (30.0, 35.0, "Obese Class I"),
        (35.0, 40.0, "Obese Class II"), 
        (40.0, 100.0, "Obese Class III")
    ]
    
    def __post_init__(self):
        self._normalize_data()
        self._calculate_bmi_and_category()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientData":
        # Get the expected field names from the dataclass
        field_names = {f.name for f in fields(cls)}
        
        # Filter out keys that aren't part of the dataclass fields
        clean_data = {
            k: v for k, v in data.items() 
            if k in field_names and k not in {'bmi', 'bmi_category'}
        }
        return cls(**clean_data)
    
    def _normalize_data(self):
        if isinstance(self.gender, str):
            self.gender = self.gender.lower().strip()
        
        # numeric type coercion for UI compatibility:
        def safe_float(x):
            try:
                return float(x) if x is not None else x
            except (ValueError, TypeError):
                return x
        
        def safe_int(x):
            try:
                return int(float(x)) if x is not None else x
            except (ValueError, TypeError):
                return x
        
        self.height_cm = safe_float(self.height_cm)
        self.weight_kg = safe_float(self.weight_kg)
        self.waist_circumference = safe_int(self.waist_circumference)
        self.systolic_bp = safe_int(self.systolic_bp)
        self.diastolic_bp = safe_int(self.diastolic_bp)
        self.total_cholesterol = safe_int(self.total_cholesterol)
        self.hdl_cholesterol = safe_int(self.hdl_cholesterol)

        # Normalize family diabetes history with comprehensive mapping
        history_aliases = {
            'no': 'none', 'none': 'none', 'false': 'none', '0': 'none',
            'grandparent': 'grandparent_aunt_uncle_cousin',
            'aunt': 'grandparent_aunt_uncle_cousin', 'uncle': 'grandparent_aunt_uncle_cousin',
            'cousin': 'grandparent_aunt_uncle_cousin', 'extended': 'grandparent_aunt_uncle_cousin',
            'parent': 'parent_sibling_child', 'mother': 'parent_sibling_child', 'father': 'parent_sibling_child',
            'sibling': 'parent_sibling_child', 'brother': 'parent_sibling_child', 'sister': 'parent_sibling_child',
            'child': 'parent_sibling_child', 'immediate': 'parent_sibling_child'
        }
        
        history_key = str(self.family_diabetes_history).lower().strip()
        if history_key in history_aliases:
            self.family_diabetes_history = history_aliases[history_key]
    
    def _calculate_bmi_and_category(self):
        if self.height_cm and self.weight_kg and self.height_cm > 0 and self.weight_kg > 0:
            height_m = self.height_cm / 100.0
            self.bmi = round(self.weight_kg / (height_m * height_m), 1)
            
            self.bmi_category = "Unknown"
            for min_bmi, max_bmi, category in self.BMI_CATEGORIES:
                if min_bmi <= self.bmi < max_bmi:
                    self.bmi_category = category
                    break
        else:
            self.bmi = None
            self.bmi_category = "Cannot Calculate"
    
    def validate(self) -> List[str]:
        """Comprehensive validation with clinical ranges."""
        errors = []
        
        if not isinstance(self.age, int) or not (18 <= self.age <= 100):
            errors.append("Age must be integer between 18-100 years")
        
        if self.gender not in ['male', 'female']:
            errors.append("Gender must be 'male' or 'female'")
        
        if not isinstance(self.height_cm, (int, float)) or not (100 <= self.height_cm <= 250):
            errors.append("Height must be between 100-250 cm")
        
        if not isinstance(self.weight_kg, (int, float)) or not (30 <= self.weight_kg <= 300):
            errors.append("Weight must be between 30-300 kg")
        
        if self.bmi is not None and not (12.0 <= self.bmi <= 60.0):
            errors.append(f"Calculated BMI ({self.bmi}) is outside clinical range (12.0-60.0)")
        elif self.bmi is None and self.height_cm and self.weight_kg:
            errors.append("BMI calculation failed despite having height and weight")
        
        if self.waist_circumference is not None and not (40 <= self.waist_circumference <= 200):
            errors.append("Waist circumference must be between 40-200 cm")
        
        if self.systolic_bp is not None and not (70 <= self.systolic_bp <= 250):
            errors.append("Systolic BP must be between 70-250 mmHg")
        
        if self.diastolic_bp is not None and not (40 <= self.diastolic_bp <= 150):
            errors.append("Diastolic BP must be between 40-150 mmHg")
        
        if self.total_cholesterol is not None and not (100 <= self.total_cholesterol <= 500):
            errors.append("Total cholesterol must be between 100-500 mg/dL")
        
        if self.hdl_cholesterol is not None and not (15 <= self.hdl_cholesterol <= 100):
            errors.append("HDL cholesterol must be between 15-100 mg/dL")
        
        valid_history = ['none', 'grandparent_aunt_uncle_cousin', 'parent_sibling_child']
        if self.family_diabetes_history not in valid_history:
            errors.append(f"Family diabetes history must be one of: {valid_history}")
        
        if self.family_colorectal_age is not None and not (20 <= self.family_colorectal_age <= 100):
            errors.append("Family colorectal cancer age must be between 20-100 years")
        
        if self.family_colorectal_cancer and self.family_colorectal_age is None:
            errors.append("Family colorectal cancer age is required when family history is positive")
            
        if self.previous_screening_date:
            try:
                from datetime import datetime
                datetime.strptime(self.previous_screening_date, "%Y-%m-%d")
            except ValueError:
                errors.append("Previous screening date must be in YYYY-MM-DD format")

        return errors
    
    def to_calculator_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for calculator consumption."""
        return {
            # Core data with calculated BMI
            'age': self.age,
            'gender': self.gender,
            'bmi': self.bmi,  
            'waist_circumference': self.waist_circumference,
            
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            
            'systolic_bp': self.systolic_bp,
            'diastolic_bp': self.diastolic_bp,
            'total_cholesterol': self.total_cholesterol,
            'hdl_cholesterol': self.hdl_cholesterol,
            
            # Medical history with calculator-friendly aliases
            'family_diabetes_history': self.family_diabetes_history,
            'high_glucose_history': self.high_glucose_history,
            'diabetes': self.diabetes_diagnosed,  # Framingham uses 'diabetes'
            'hypertension_medication': self.hypertension_medication,
            'on_bp_medication': self.hypertension_medication,  # Framingham alias
            'current_smoker': self.current_smoker,
            
            # Cancer screening history
            'family_history_first_degree': self.family_colorectal_cancer,
            'family_history_age': self.family_colorectal_age,
            'personal_history_polyps': self.personal_history_polyps,
            'inflammatory_bowel_disease': self.inflammatory_bowel_disease,
            'high_risk_syndrome': self.high_risk_syndrome,
            'previous_screening_date': self.previous_screening_date,
            'previous_screening_method': self.previous_screening_method,
            
            'physical_activity': self.physical_activity,
            'vegetable_fruit_daily': self.vegetable_fruit_daily
        }
    
    def summary(self) -> str:
        """Human-readable patient summary."""
        bmi_info = f", BMI: {self.bmi} ({self.bmi_category})" if self.bmi else ", BMI: N/A"
        return f"{self.age}yo {self.gender.title()}, {self.height_cm}cm/{self.weight_kg}kg{bmi_info}"
    
    def clinical_summary(self) -> str:
        """Clinical summary highlighting key risk factors."""
        base_summary = self.summary()
        
        risk_factors = []
        
        # BMI-related risks
        if self.bmi:
            if self.bmi >= 30:
                risk_factors.append(f"Obese ({self.bmi_category})")
            elif self.bmi >= 25:
                risk_factors.append("Overweight")
        
        # Medical history risks
        if self.current_smoker:
            risk_factors.append("Current smoker")
        if self.diabetes_diagnosed:
            risk_factors.append("Diabetes")
        if self.hypertension_medication:
            risk_factors.append("Hypertension")
        if self.family_diabetes_history != 'none':
            risk_factors.append("Family diabetes history")
        if self.high_glucose_history:
            risk_factors.append("Prior high glucose")
        
        # Lifestyle risks
        if not self.physical_activity:
            risk_factors.append("Sedentary")
        if not self.vegetable_fruit_daily:
            risk_factors.append("Poor diet")
        
        if risk_factors:
            return f"{base_summary} | Risk factors: {', '.join(risk_factors)}"
        else:
            return f"{base_summary} | No major risk factors identified"

# Updated test scenarios with height/weight instead of BMI
def get_test_scenarios() -> Dict[str, Dict[str, Any]]:
    """Predefined patient scenarios with height/weight for BMI calculation."""
    
    return {
        'low_risk_young_female': {
            'age': 32, 'gender': 'female', 
            'height_cm': 165, 'weight_kg': 58,  # BMI: 21.3 (Normal Weight)
            'waist_circumference': 75, 'systolic_bp': 110, 'diastolic_bp': 70,
            'total_cholesterol': 175, 'hdl_cholesterol': 68,
            'physical_activity': True, 'vegetable_fruit_daily': True,
            'current_smoker': False, 'family_diabetes_history': 'none'
        },
        
        'high_risk_middle_aged_male': {
            'age': 52, 'gender': 'male', 
            'height_cm': 175, 'weight_kg': 95,  # BMI: 31.0 (Obese Class I)
            'waist_circumference': 105, 'systolic_bp': 145, 'diastolic_bp': 92,
            'total_cholesterol': 240, 'hdl_cholesterol': 35,
            'diabetes_diagnosed': False, 'hypertension_medication': True,
            'high_glucose_history': True, 'current_smoker': True,
            'physical_activity': False, 'vegetable_fruit_daily': False,
            'family_diabetes_history': 'parent_sibling_child',
            'family_colorectal_cancer': True, 'family_colorectal_age': 58
        },
        
        'elderly_screening_candidate': {
            'age': 68, 'gender': 'female', 
            'height_cm': 160, 'weight_kg': 70,  # BMI: 27.3 (Overweight)
            'waist_circumference': 85, 'systolic_bp': 135, 'diastolic_bp': 85,
            'total_cholesterol': 200, 'hdl_cholesterol': 50,
            'diabetes_diagnosed': True, 'hypertension_medication': True,
            'current_smoker': False, 'physical_activity': True,
            'previous_screening_date': '2018-03-15', 'previous_screening_method': 'colonoscopy'
        },
        
        'borderline_overweight_active': {
            'age': 45, 'gender': 'male',
            'height_cm': 180, 'weight_kg': 85,  # BMI: 26.2 (Overweight)
            'waist_circumference': 95, 'systolic_bp': 125, 'diastolic_bp': 80,
            'total_cholesterol': 210, 'hdl_cholesterol': 45,
            'physical_activity': True, 'vegetable_fruit_daily': True,
            'current_smoker': False, 'family_diabetes_history': 'grandparent'
        }
    }

if __name__ == "__main__":
    scenarios = get_test_scenarios()
    test_patient = PatientData.from_dict(scenarios['high_risk_middle_aged_male'])
    
    print(f" PatientData: {test_patient.summary()}")
    print(f" BMI Calculation: {test_patient.bmi} ({test_patient.bmi_category})")
    
    errors = test_patient.validate()
    if errors:
        print(f" Validation: {len(errors)} errors found")
    else:
        print(f" Validation: All checks passed")
    
    calc_data = test_patient.to_calculator_dict()
    print(f" Calculator Export: {len(calc_data)} fields ready")