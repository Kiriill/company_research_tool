from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class CompanySelection(BaseModel):
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    score: float = 0.0
    slug: Optional[str] = None


class ReportSection(BaseModel):
    title: str
    content: str
    sources: List[str] = Field(default_factory=list)


class ReportData(BaseModel):
    company_title: str
    slug: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    founded: Optional[str] = None
    employees: Optional[str] = None
    website: Optional[str] = None

    leaders: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)
    revenue: Optional[str] = None

    sections: List[ReportSection] = Field(default_factory=list)
    peers: List[str] = Field(default_factory=list)
    differentiation: Optional[str] = None

    references: List[str] = Field(default_factory=list)

    meta: Dict[str, Any] = Field(default_factory=dict)