import React, { useState, useEffect } from 'react';
import { validateInsight, InsightValidation, InsightData } from '../utils/retailbot';
import { logMemory } from '../utils/memory';

interface InsightCardProps {
  title: string;
  data: InsightData;
  type: 'metric' | 'trend' | 'comparison' | 'forecast';
  description?: string;
  source?: string;
  onValidationComplete?: (validation: InsightValidation) => void;
  enableRetailBotValidation?: boolean;
}

interface ValidationIndicatorProps {
  validation: InsightValidation;
  showDetails: boolean;
  onToggleDetails: () => void;
}

const ValidationIndicator: React.FC<ValidationIndicatorProps> = ({
  validation,
  showDetails,
  onToggleDetails
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validated': return 'text-green-600 bg-green-50';
      case 'warning': return 'text-yellow-600 bg-yellow-50';
      case 'error': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'validated': return '✓';
      case 'warning': return '⚠';
      case 'error': return '✗';
      default: return '?';
    }
  };

  return (
    <div className="mt-2">
      <button
        onClick={onToggleDetails}
        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium transition-colors ${getStatusColor(validation.status)}`}
      >
        <span className="mr-1">{getStatusIcon(validation.status)}</span>
        RetailBot {validation.status === 'validated' ? 'Verified' : validation.status}
        <span className="ml-1">{showDetails ? '↑' : '↓'}</span>
      </button>
      
      {showDetails && (
        <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Confidence:</span>
              <span className="text-sm text-gray-600">{(validation.confidence * 100).toFixed(1)}%</span>
            </div>
            
            {validation.checks && (
              <div className="space-y-1">
                <span className="text-sm font-medium text-gray-700">Validation Checks:</span>
                {validation.checks.map((check, index) => (
                  <div key={index} className="flex items-center space-x-2 text-xs">
                    <span className={check.passed ? 'text-green-600' : 'text-red-600'}>
                      {check.passed ? '✓' : '✗'}
                    </span>
                    <span className="text-gray-600">{check.name}</span>
                  </div>
                ))}
              </div>
            )}
            
            {validation.suggestions && validation.suggestions.length > 0 && (
              <div className="space-y-1">
                <span className="text-sm font-medium text-gray-700">Suggestions:</span>
                <ul className="text-xs text-gray-600 space-y-1">
                  {validation.suggestions.map((suggestion, index) => (
                    <li key={index} className="flex items-start space-x-1">
                      <span className="text-blue-500 mt-0.5">•</span>
                      <span>{suggestion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {validation.alternativeViews && validation.alternativeViews.length > 0 && (
              <div className="space-y-1">
                <span className="text-sm font-medium text-gray-700">Alternative Views:</span>
                <div className="flex flex-wrap gap-1">
                  {validation.alternativeViews.map((view, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      {view}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
              Validated at {new Date(validation.timestamp).toLocaleString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const InsightCard: React.FC<InsightCardProps> = ({
  title,
  data,
  type,
  description,
  source,
  onValidationComplete,
  enableRetailBotValidation = true
}) => {
  const [validation, setValidation] = useState<InsightValidation | null>(null);
  const [validating, setValidating] = useState(false);
  const [showValidationDetails, setShowValidationDetails] = useState(false);
  const [error, setError] = useState<string>('');

  // Auto-validate when component mounts or data changes
  useEffect(() => {
    if (enableRetailBotValidation && data) {
      performValidation();
    }
  }, [data, enableRetailBotValidation]);

  const performValidation = async () => {
    setValidating(true);
    setError('');
    
    try {
      const validationResult = await validateInsight(data, type);
      setValidation(validationResult);
      
      // Log validation result for analytics
      await logMemory('retailbot-validations', {
        title,
        type,
        validation: validationResult,
        timestamp: new Date().toISOString()
      });
      
      // Callback to parent component
      if (onValidationComplete) {
        onValidationComplete(validationResult);
      }
      
    } catch (err) {
      setError('Validation failed. RetailBot is currently unavailable.');
      console.error('RetailBot validation error:', err);
    } finally {
      setValidating(false);
    }
  };

  const formatValue = (value: any): string => {
    if (typeof value === 'number') {
      if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M`;
      } else if (value >= 1000) {
        return `${(value / 1000).toFixed(1)}K`;
      }
      return value.toLocaleString();
    }
    return String(value);
  };

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'metric': return '📊';
      case 'trend': return '📈';
      case 'comparison': return '⚖️';
      case 'forecast': return '🔮';
      default: return '📋';
    }
  };

  const getInsightColor = (type: string): string => {
    switch (type) {
      case 'metric': return 'border-blue-200 bg-blue-50';
      case 'trend': return 'border-green-200 bg-green-50';
      case 'comparison': return 'border-purple-200 bg-purple-50';
      case 'forecast': return 'border-orange-200 bg-orange-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className={`p-4 rounded-lg border-2 transition-all hover:shadow-md ${getInsightColor(type)}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <span className="text-lg">{getTypeIcon(type)}</span>
          <h3 className="font-semibold text-gray-800">{title}</h3>
        </div>
        
        {enableRetailBotValidation && (
          <button
            onClick={performValidation}
            disabled={validating}
            className="text-xs px-2 py-1 bg-white border border-gray-300 rounded hover:bg-gray-50 disabled:opacity-50"
          >
            {validating ? '⟳' : '🤖'} Validate
          </button>
        )}
      </div>

      {/* Main Content */}
      <div className="space-y-3">
        {/* Primary Value */}
        {data.value !== undefined && (
          <div className="text-2xl font-bold text-gray-900">
            {formatValue(data.value)}
            {data.unit && <span className="text-sm font-normal text-gray-600 ml-1">{data.unit}</span>}
          </div>
        )}

        {/* Change Indicator */}
        {data.change !== undefined && (
          <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-medium ${
            data.change > 0 
              ? 'text-green-700 bg-green-100' 
              : data.change < 0 
              ? 'text-red-700 bg-red-100'
              : 'text-gray-700 bg-gray-100'
          }`}>
            <span className="mr-1">
              {data.change > 0 ? '↗' : data.change < 0 ? '↘' : '→'}
            </span>
            {Math.abs(data.change)}% {data.changePeriod || 'vs previous period'}
          </div>
        )}

        {/* Description */}
        {description && (
          <p className="text-sm text-gray-600 leading-relaxed">{description}</p>
        )}

        {/* Additional Metrics */}
        {data.additionalMetrics && (
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-200">
            {Object.entries(data.additionalMetrics).map(([key, value]) => (
              <div key={key} className="text-center">
                <div className="text-lg font-semibold text-gray-800">{formatValue(value)}</div>
                <div className="text-xs text-gray-600 capitalize">{key.replace(/([A-Z])/g, ' $1')}</div>
              </div>
            ))}
          </div>
        )}

        {/* Source */}
        {source && (
          <div className="text-xs text-gray-500">
            Source: {source}
          </div>
        )}

        {/* Validation Status */}
        {enableRetailBotValidation && (
          <>
            {validating && (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                <span>RetailBot is validating...</span>
              </div>
            )}
            
            {error && (
              <div className="text-sm text-red-600 bg-red-50 p-2 rounded border border-red-200">
                {error}
              </div>
            )}
            
            {validation && !validating && (
              <ValidationIndicator
                validation={validation}
                showDetails={showValidationDetails}
                onToggleDetails={() => setShowValidationDetails(!showValidationDetails)}
              />
            )}
          </>
        )}
      </div>
    </div>
  );
};