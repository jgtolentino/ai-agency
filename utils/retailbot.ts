// RetailBot Validation System - AI-powered insight card validation
import { logMemory } from './memory';

export interface InsightData {
  value?: number | string;
  unit?: string;
  change?: number;
  changePeriod?: string;
  additionalMetrics?: Record<string, number | string>;
  dataSource?: string;
  calculationMethod?: string;
  sampleSize?: number;
  confidence?: number;
  timeRange?: {
    start: string;
    end: string;
  };
}

export interface ValidationCheck {
  name: string;
  passed: boolean;
  details?: string;
}

export interface InsightValidation {
  status: 'validated' | 'warning' | 'error';
  confidence: number;
  timestamp: string;
  checks?: ValidationCheck[];
  suggestions?: string[];
  alternativeViews?: string[];
  retailBotAnalysis?: string;
}

// Validation rules for different insight types
const VALIDATION_RULES = {
  metric: {
    requiredFields: ['value'],
    validRanges: {
      percentage: { min: 0, max: 100 },
      currency: { min: 0, max: Infinity },
      count: { min: 0, max: Infinity }
    },
    warningThresholds: {
      highVolatility: 50, // % change threshold
      lowSampleSize: 100
    }
  },
  trend: {
    requiredFields: ['value', 'change'],
    validRanges: {
      change: { min: -1000, max: 1000 } // % change limits
    },
    warningThresholds: {
      extremeChange: 100,
      inconsistentTrend: 30
    }
  },
  comparison: {
    requiredFields: ['value', 'additionalMetrics'],
    validRanges: {},
    warningThresholds: {
      lowComparisons: 2
    }
  },
  forecast: {
    requiredFields: ['value', 'confidence'],
    validRanges: {
      confidence: { min: 0, max: 1 }
    },
    warningThresholds: {
      lowConfidence: 0.7,
      longForecast: 365 // days
    }
  }
};

// Data quality checks
function performDataQualityChecks(data: InsightData, type: string): ValidationCheck[] {
  const checks: ValidationCheck[] = [];
  const rules = VALIDATION_RULES[type as keyof typeof VALIDATION_RULES];

  // Check required fields
  for (const field of rules.requiredFields) {
    checks.push({
      name: `Required field: ${field}`,
      passed: data[field as keyof InsightData] !== undefined,
      details: data[field as keyof InsightData] ? 'Present' : 'Missing'
    });
  }

  // Check data ranges
  if (typeof data.value === 'number') {
    // Detect probable data type based on value characteristics
    let dataType = 'count';
    if (data.unit?.includes('%') || (data.value >= 0 && data.value <= 100 && !data.unit)) {
      dataType = 'percentage';
    } else if (data.unit?.includes('$') || data.unit?.includes('₱') || data.unit?.includes('currency')) {
      dataType = 'currency';
    }

    const range = rules.validRanges[dataType as keyof typeof rules.validRanges];
    if (range) {
      checks.push({
        name: `Value range check (${dataType})`,
        passed: data.value >= range.min && data.value <= range.max,
        details: `Value: ${data.value}, Expected: ${range.min}-${range.max}`
      });
    }
  }

  // Check change values for trends
  if (type === 'trend' && typeof data.change === 'number') {
    const changeRange = rules.validRanges.change;
    checks.push({
      name: 'Change value reasonableness',
      passed: Math.abs(data.change) <= changeRange.max,
      details: `Change: ${data.change}%, Threshold: ±${changeRange.max}%`
    });
  }

  // Check confidence for forecasts
  if (type === 'forecast' && typeof data.confidence === 'number') {
    const confRange = rules.validRanges.confidence;
    checks.push({
      name: 'Confidence score validity',
      passed: data.confidence >= confRange.min && data.confidence <= confRange.max,
      details: `Confidence: ${data.confidence}, Expected: ${confRange.min}-${confRange.max}`
    });
  }

  // Sample size check
  if (data.sampleSize !== undefined) {
    checks.push({
      name: 'Sample size adequacy',
      passed: data.sampleSize >= rules.warningThresholds.lowSampleSize,
      details: `Sample size: ${data.sampleSize}, Minimum: ${rules.warningThresholds.lowSampleSize}`
    });
  }

  return checks;
}

// Business logic validation
function performBusinessLogicChecks(data: InsightData, type: string): ValidationCheck[] {
  const checks: ValidationCheck[] = [];

  // Seasonal consistency check for retail metrics
  if (type === 'metric' || type === 'trend') {
    const currentMonth = new Date().getMonth();
    const isHolidaySeason = currentMonth === 11 || currentMonth === 0; // Dec or Jan
    
    if (isHolidaySeason && typeof data.change === 'number' && data.change < -20) {
      checks.push({
        name: 'Holiday season performance',
        passed: false,
        details: `Significant decline (${data.change}%) during holiday season needs review`
      });
    } else {
      checks.push({
        name: 'Seasonal consistency',
        passed: true,
        details: 'Performance aligns with seasonal expectations'
      });
    }
  }

  // Cross-metric consistency
  if (data.additionalMetrics) {
    const metrics = Object.entries(data.additionalMetrics);
    let consistencyScore = 0;
    let totalChecks = 0;

    // Example: Revenue vs Units relationship
    const revenue = metrics.find(([key]) => key.toLowerCase().includes('revenue'))?.[1];
    const units = metrics.find(([key]) => key.toLowerCase().includes('units'))?.[1];
    
    if (revenue && units && typeof revenue === 'number' && typeof units === 'number') {
      const avgPrice = revenue / units;
      consistencyScore += avgPrice > 0 ? 1 : 0;
      totalChecks++;
    }

    checks.push({
      name: 'Cross-metric consistency',
      passed: totalChecks === 0 || consistencyScore / totalChecks >= 0.8,
      details: `${consistencyScore}/${totalChecks} metric relationships validated`
    });
  }

  return checks;
}

// Generate suggestions based on validation results
function generateSuggestions(data: InsightData, type: string, checks: ValidationCheck[]): string[] {
  const suggestions: string[] = [];
  const failedChecks = checks.filter(check => !check.passed);

  if (failedChecks.length === 0) {
    suggestions.push('Data quality looks excellent! Consider adding trend comparisons for deeper insights.');
    return suggestions;
  }

  // Specific suggestions based on failed checks
  failedChecks.forEach(check => {
    switch (check.name) {
      case 'Required field: change':
        suggestions.push('Add period-over-period change to show trend direction and magnitude.');
        break;
      case 'Required field: confidence':
        suggestions.push('Include confidence interval for forecast reliability assessment.');
        break;
      case 'Sample size adequacy':
        suggestions.push('Increase sample size or add confidence intervals for more reliable insights.');
        break;
      case 'Change value reasonableness':
        suggestions.push('Verify data sources - extreme changes may indicate data quality issues.');
        break;
      case 'Holiday season performance':
        suggestions.push('Investigate factors causing holiday season decline - consider competitor analysis.');
        break;
      default:
        suggestions.push(`Review ${check.name.toLowerCase()} to improve data quality.`);
    }
  });

  // General improvement suggestions
  if (type === 'metric' && !data.change) {
    suggestions.push('Add trend analysis to provide context for current performance.');
  }

  if (!data.additionalMetrics) {
    suggestions.push('Include supporting metrics for comprehensive analysis.');
  }

  if (!data.timeRange) {
    suggestions.push('Specify time range for better insight interpretation.');
  }

  return suggestions.slice(0, 3); // Limit to top 3 suggestions
}

// Generate alternative view suggestions
function generateAlternativeViews(data: InsightData, type: string): string[] {
  const alternatives: string[] = [];

  switch (type) {
    case 'metric':
      alternatives.push('Trend View', 'Comparison Chart', 'Geographic Breakdown');
      break;
    case 'trend':
      alternatives.push('Seasonal Analysis', 'Cohort View', 'Correlation Matrix');
      break;
    case 'comparison':
      alternatives.push('Ranking Table', 'Performance Matrix', 'Relative Growth');
      break;
    case 'forecast':
      alternatives.push('Scenario Analysis', 'Confidence Bands', 'Historical Accuracy');
      break;
  }

  return alternatives;
}

// Main validation function
export async function validateInsight(data: InsightData, type: string): Promise<InsightValidation> {
  try {
    // Perform validation checks
    const dataQualityChecks = performDataQualityChecks(data, type);
    const businessLogicChecks = performBusinessLogicChecks(data, type);
    const allChecks = [...dataQualityChecks, ...businessLogicChecks];

    // Calculate overall status and confidence
    const passedChecks = allChecks.filter(check => check.passed).length;
    const totalChecks = allChecks.length;
    const passRate = totalChecks > 0 ? passedChecks / totalChecks : 1;

    let status: 'validated' | 'warning' | 'error';
    if (passRate >= 0.9) {
      status = 'validated';
    } else if (passRate >= 0.7) {
      status = 'warning';
    } else {
      status = 'error';
    }

    // Generate suggestions and alternatives
    const suggestions = generateSuggestions(data, type, allChecks);
    const alternativeViews = generateAlternativeViews(data, type);

    // Create RetailBot analysis summary
    const retailBotAnalysis = generateRetailBotAnalysis(data, type, passRate, allChecks);

    const validation: InsightValidation = {
      status,
      confidence: passRate,
      timestamp: new Date().toISOString(),
      checks: allChecks,
      suggestions,
      alternativeViews,
      retailBotAnalysis
    };

    // Log validation for analytics and learning
    await logMemory('retailbot-validation-results', {
      type,
      dataCharacteristics: {
        hasValue: data.value !== undefined,
        hasChange: data.change !== undefined,
        hasAdditionalMetrics: !!data.additionalMetrics,
        hasTimeRange: !!data.timeRange
      },
      validation,
      timestamp: new Date().toISOString()
    });

    return validation;

  } catch (error) {
    console.error('RetailBot validation error:', error);
    
    return {
      status: 'error',
      confidence: 0,
      timestamp: new Date().toISOString(),
      suggestions: ['Validation service temporarily unavailable. Please try again later.'],
      retailBotAnalysis: 'Unable to perform validation due to service error.'
    };
  }
}

// Generate RetailBot analysis summary
function generateRetailBotAnalysis(data: InsightData, type: string, passRate: number, checks: ValidationCheck[]): string {
  const criticalIssues = checks.filter(check => !check.passed && check.name.includes('Required')).length;
  const warningIssues = checks.filter(check => !check.passed && !check.name.includes('Required')).length;

  if (passRate >= 0.9) {
    return `Excellent data quality detected. This ${type} insight meets all validation criteria and provides reliable business intelligence for decision-making.`;
  } else if (passRate >= 0.7) {
    return `Good data quality with minor concerns. ${warningIssues} warning(s) identified. The insight is usable but could benefit from addressing the suggested improvements.`;
  } else if (criticalIssues > 0) {
    return `Critical data issues detected. ${criticalIssues} required field(s) missing. Please address these issues before using this insight for business decisions.`;
  } else {
    return `Multiple data quality concerns identified. While the insight may provide directional guidance, additional validation is recommended before making strategic decisions.`;
  }
}

// Get RetailBot recommendations for insight improvement
export async function getInsightRecommendations(type: string, currentMetrics?: string[]): Promise<string[]> {
  const recommendations: Record<string, string[]> = {
    'metric': [
      'Add period-over-period comparison',
      'Include confidence intervals',
      'Provide regional breakdown',
      'Show seasonal trends'
    ],
    'trend': [
      'Extend historical data range',
      'Add statistical significance testing',
      'Include external factor analysis',
      'Compare with industry benchmarks'
    ],
    'comparison': [
      'Add more comparison dimensions',
      'Include market share context',
      'Show competitive positioning',
      'Provide normalization options'
    ],
    'forecast': [
      'Include multiple scenarios',
      'Add uncertainty quantification',
      'Provide model accuracy metrics',
      'Show historical forecast performance'
    ]
  };

  return recommendations[type] || ['Add more contextual information', 'Include data source details'];
}

// Check if RetailBot validation is available for specific data types
export function isValidationAvailable(dataType: string): boolean {
  return Object.keys(VALIDATION_RULES).includes(dataType);
}