// TanStack Query hooks for strategies
export * from "@/client/@tanstack/react-query.gen";

// Re-export commonly used strategy hooks with better names
export {
    strategiesCreateStrategyMutation, strategiesDeleteStrategyMutation,
    strategiesExecuteStrategyMutation, strategiesGetStrategiesQueryKey, strategiesGetStrategyExecutionsQueryKey, strategiesGetStrategyPerformanceQueryKey, strategiesGetStrategyQueryKey, strategiesUpdateStrategyMutation, strategiesGetStrategiesOptions as useStrategiesQuery, strategiesGetStrategyExecutionsOptions as useStrategyExecutionsQuery, strategiesGetStrategyPerformanceOptions as useStrategyPerformanceQuery, strategiesGetStrategyOptions as useStrategyQuery
} from "@/client/@tanstack/react-query.gen";

// Re-export commonly used template hooks
export {
    templatesCreateStrategyFromTemplateMutation,
    templatesCreateTemplateMutation,
    templatesDeleteTemplateMutation, templatesGetTemplateQueryKey, templatesGetTemplatesQueryKey,
    templatesGetTemplateOptions as useTemplateQuery, templatesGetTemplatesOptions as useTemplatesQuery
} from "@/client/@tanstack/react-query.gen";

// Utility functions for strategies
export const strategyUtils = {
    formatStrategyType: (type: string): string => {
        const typeMap: Record<string, string> = {
            sma_crossover: "SMA 크로스오버",
            rsi_mean_reversion: "RSI 평균회귀",
            momentum: "모멘텀",
            buy_and_hold: "매수후보유",
        };
        return typeMap[type] || type;
    },

    getStrategyTypeColor: (type: string): "primary" | "secondary" | "info" | "success" | "default" => {
        const colorMap: Record<string, "primary" | "secondary" | "info" | "success" | "default"> = {
            sma_crossover: "primary",
            rsi_mean_reversion: "secondary",
            momentum: "info",
            buy_and_hold: "success",
        };
        return colorMap[type] || "default";
    },

    getDifficultyColor: (difficulty?: string): "success" | "warning" | "error" | "default" => {
        switch (difficulty?.toLowerCase()) {
            case "초급":
                return "success";
            case "중급":
                return "warning";
            case "고급":
                return "error";
            default:
                return "default";
        }
    },

    validateParameters: (
        parameters: Record<string, any>,
        schema?: Record<string, any>
    ): { isValid: boolean; errors: Record<string, string> } => {
        const errors: Record<string, string> = {};

        if (!schema) {
            return { isValid: true, errors };
        }

        Object.entries(schema).forEach(([key, paramSchema]) => {
            const value = parameters[key];

            if (paramSchema.required && (value === undefined || value === null || value === "")) {
                errors[key] = "필수 항목입니다.";
                return;
            }

            if (paramSchema.type === "number" && value !== undefined) {
                const numValue = Number(value);
                if (isNaN(numValue)) {
                    errors[key] = "숫자를 입력해주세요.";
                    return;
                }
                if (paramSchema.min !== undefined && numValue < paramSchema.min) {
                    errors[key] = `최소값은 ${paramSchema.min}입니다.`;
                    return;
                }
                if (paramSchema.max !== undefined && numValue > paramSchema.max) {
                    errors[key] = `최대값은 ${paramSchema.max}입니다.`;
                    return;
                }
            }
        });

        return {
            isValid: Object.keys(errors).length === 0,
            errors,
        };
    },

    // 기본 파라미터 스키마 (백엔드에서 오지 않을 경우 대비)
    getDefaultParameterSchema: (strategyType: string): Record<string, any> => {
        const DEFAULT_SCHEMAS: Record<string, Record<string, any>> = {
            sma_crossover: {
                short_window: {
                    type: "number",
                    description: "단기 이동평균 기간",
                    min: 5,
                    max: 50,
                    step: 1,
                    default: 20,
                    required: true,
                },
                long_window: {
                    type: "number",
                    description: "장기 이동평균 기간",
                    min: 20,
                    max: 200,
                    step: 1,
                    default: 50,
                    required: true,
                },
            },
            rsi_mean_reversion: {
                rsi_period: {
                    type: "number",
                    description: "RSI 계산 기간",
                    min: 5,
                    max: 30,
                    step: 1,
                    default: 14,
                    required: true,
                },
                oversold_threshold: {
                    type: "number",
                    description: "과매도 임계값",
                    min: 10,
                    max: 40,
                    step: 1,
                    default: 30,
                    required: true,
                },
                overbought_threshold: {
                    type: "number",
                    description: "과매수 임계값",
                    min: 60,
                    max: 90,
                    step: 1,
                    default: 70,
                    required: true,
                },
            },
            momentum: {
                lookback_period: {
                    type: "number",
                    description: "모멘텀 계산 기간",
                    min: 5,
                    max: 50,
                    step: 1,
                    default: 12,
                    required: true,
                },
                threshold: {
                    type: "number",
                    description: "모멘텀 임계값 (%)",
                    min: 1,
                    max: 20,
                    step: 0.5,
                    default: 5,
                    required: true,
                },
            },
            buy_and_hold: {
                initial_investment: {
                    type: "number",
                    description: "초기 투자금액",
                    min: 1000,
                    max: 1000000,
                    step: 1000,
                    default: 10000,
                    required: true,
                },
            },
        };

        return DEFAULT_SCHEMAS[strategyType] || {};
    },
};
